import os
import time
import math
import json
import mimetypes
from typing import List, Union
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from urllib.error import HTTPError

from cat.log import log
from starlette.datastructures import UploadFile
from langchain.docstore.document import Document
from qdrant_client.http import models

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders.parsers import PDFMinerParser
from langchain.document_loaders.parsers.generic import MimeTypeBasedParser
from langchain.document_loaders.parsers.txt import TextParser
from langchain.document_loaders.blob_loaders.schema import Blob
from langchain.document_loaders.parsers.html.bs4 import BS4HTMLParser


class RabbitHole:
    """Manages content ingestion. I'm late... I'm late!
    """

    def __init__(self, cat):
        self.cat = cat

        file_handlers = {
            "application/pdf": PDFMinerParser(),
            "text/plain": TextParser(),
            "text/markdown": TextParser(),
            "text/html": BS4HTMLParser()
        }

        self.file_handlers = cat.mad_hatter.execute_hook("rabbithole_instantiates_parsers", file_handlers)

    def ingest_memory(self, file: UploadFile):
        """Upload memories to the declarative memory from a JSON file.

        Parameters
        ----------
        file : UploadFile
            File object sent via `rabbithole/memory` hook.

        Notes
        -----
        This method allows uploading a JSON file containing vector and text memories directly to the declarative memory.
        When doing this, please, make sure the embedder used to export the memories is the same as the one used
        when uploading.
        The method also performs a check on the dimensionality of the embeddings (i.e. length of each vector).

        """

        # Get file bytes
        file_bytes = file.file.read()

        # Load fyle byte in a dict
        memories = json.loads(file_bytes.decode("utf-8"))

        # Check the embedder used for the uploaded memories is the same the Cat is using now
        upload_embedder = memories["embedder"]
        cat_embedder = str(self.cat.embedder.__class__.__name__)

        if upload_embedder != cat_embedder:
            message = f'Embedder mismatch: file embedder {upload_embedder} is different from {cat_embedder}'
            raise Exception(message)

        # Get Declarative memories in file
        declarative_memories = memories["collections"]["declarative"]

        # Store data to upload the memories in batch
        ids = [i["id"] for i in declarative_memories]
        payloads = [{
            "page_content": p["page_content"],
            "metadata": p["metadata"]
        } for p in declarative_memories]
        vectors = [v["vector"] for v in declarative_memories]

        log.info(f"Preparing to load {len(vectors)} vector memories")

        # Check embedding size is correct
        embedder_size = self.cat.memory.vectors.embedder_size
        len_mismatch = [len(v) == embedder_size for v in vectors]

        if not any(len_mismatch):
            message = f'Embedding size mismatch: vectors length should be {embedder_size}'
            raise Exception(message)

        # Upsert memories in batch mode # TODO: make a method for batch inserting inside vector memory
        self.cat.memory.vectors.vector_db.upsert(
            collection_name="declarative",
            points=models.Batch(
                ids=ids,
                payloads=payloads,
                vectors=vectors
            )
        )

    def ingest_file(
            self,
            file: Union[str, UploadFile],
            chunk_size: int = 400,
            chunk_overlap: int = 100
    ):
        """Load a file in the Cat's declarative memory.

        The method splits and converts the file in Langchain `Document`. Then, it stores the `Document` in the Cat's
        memory.

        Parameters
        ----------
        file : str, UploadFile
            The file can be a path passed as a string or an `UploadFile` object if the document is ingested using the
            `rabbithole` endpoint.
        chunk_size : int
            Number of characters in each document chunk.
        chunk_overlap : int
            Number of overlapping characters between consecutive chunks.

        Notes
        ----------
        Currently supported formats are `.txt`, `.pdf` and `.md`.

        See Also
        ----------
        before_rabbithole_stores_documents
        """

        # split file into a list of docs
        docs = self.file_to_docs(
            file=file, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # store in memory
        if isinstance(file, str):
            filename = file
        else:
            filename = file.filename

        self.store_documents(docs=docs, source=filename)

    def file_to_docs(
            self,
            file: Union[str, UploadFile],
            chunk_size: int = 400,
            chunk_overlap: int = 100,
    ) -> List[Document]:
        """Load and convert files to Langchain `Document`.

        This method takes a file either from a Python script, from the `/rabbithole/` or `/rabbithole/web` endpoints.
        Hence, it loads it in memory and splits it in overlapped chunks of text.

        Parameters
        ----------
        file : str, UploadFile
            The file can be either a string path if loaded programmatically, a FastAPI `UploadFile`
            if coming from the `/rabbithole/` endpoint or a URL if coming from the `/rabbithole/web` endpoint.
        chunk_size : int
            Number of characters in each document chunk.
        chunk_overlap : int
            Number of overlapping characters between consecutive chunks.

        Returns
        -------
        docs : List[Document]
            List of Langchain `Document` of chunked text.

        Notes
        -----
        This method is used by both `/rabbithole/` and `/rabbithole/web` endpoints.
        Currently supported files are `.txt`, `.pdf`, `.md` and web pages.

        """

        # Check type of incoming file.
        if isinstance(file, UploadFile):
            # Get mime type and source of UploadFile
            content_type = mimetypes.guess_type(file.filename)[0]
            source = file.filename

            # Get file bytes
            file_bytes = file.file.read()
        elif isinstance(file, str):
            # Check if string file is a string or url
            parsed_file = urlparse(file)
            is_url = all([parsed_file.scheme, parsed_file.netloc])

            if is_url:
                # Define mime type and source of url
                content_type = "text/html"
                source = file

                # Make a request with a fake browser name
                request = Request(file, headers={"User-Agent": "Magic Browser"})

                try:
                    # Get binary content of url
                    with urlopen(request) as response:
                        file_bytes = response.read()
                except HTTPError as e:
                    log.error(e)
            else:

                # Get mime type from file extension and source
                content_type = mimetypes.guess_type(file)[0]
                source = os.path.basename(file)

                # Get file bytes
                with open(file, "rb") as f:
                    file_bytes = f.read()
        else:
            raise ValueError(f"{type(file)} is not a valid type.")

        # Load the bytes in the Blob schema
        blob = Blob(data=file_bytes,
                    mimetype=content_type,
                    source=source).from_data(data=file_bytes,
                                             mime_type=content_type,
                                             path=source)
        # Parser based on the mime type
        parser = MimeTypeBasedParser(handlers=self.file_handlers)

        # Parse the text
        self.cat.send_ws_message("I'm parsing the content. Big content could require some minutes...")
        text = parser.parse(blob)

        self.cat.send_ws_message(f"Parsing completed. Now let's go with reading process...")
        docs = self.split_text(text, chunk_size, chunk_overlap)
        return docs

    def store_documents(self, docs: List[Document], source: str) -> None:
        """Add documents to the Cat's declarative memory.

        This method loops a list of Langchain `Document` and adds some metadata. Namely, the source filename and the
        timestamp of insertion. Once done, the method notifies the client via Websocket connection.

        Parameters
        ----------
        docs : List[Document]
            List of Langchain `Document` to be inserted in the Cat's declarative memory.
        source : str
            Source name to be added as a metadata. It can be a file name or an URL.

        Notes
        -------
        At this point, it is possible to customize the Cat's behavior using the `before_rabbithole_insert_memory` hook
        to edit the memories before they are inserted in the vector database.

        See Also
        --------
        before_rabbithole_insert_memory
        """

        log.info(f"Preparing to memorize {len(docs)} vectors")

        # hook the docs before they are stored in the vector memory
        docs = self.cat.mad_hatter.execute_hook(
            "before_rabbithole_stores_documents", docs
        )

        # classic embed
        time_last_notification = time.time()
        time_interval = 10  # a notification every 10 secs
        for d, doc in enumerate(docs):
            if time.time() - time_last_notification > time_interval:
                time_last_notification = time.time()
                perc_read = int(d / len(docs) * 100)
                self.cat.send_ws_message(f"Read {perc_read}% of {source}")

            doc.metadata["source"] = source
            doc.metadata["when"] = time.time()
            doc = self.cat.mad_hatter.execute_hook(
                "before_rabbithole_insert_memory", doc
            )
            inserting_info = f"{d + 1}/{len(docs)}):    {doc.page_content}"
            if doc.page_content != "":
                _ = self.cat.memory.vectors.declarative.add_texts(
                    [doc.page_content],
                    [doc.metadata],
                )

                log.info(f"Inserted into memory({inserting_info})")
            else:
                log.info(f"Skipped memory insertion of empty doc ({inserting_info})")

            # wait a little to avoid APIs rate limit errors
            time.sleep(0.1)

        # notify client
        finished_reading_message = f"Finished reading {source}, " \
                                   f"I made {len(docs)} thoughts on it."

        self.cat.send_ws_message(finished_reading_message)

        print(f"\n\nDone uploading {source}")

    def split_text(self, text, chunk_size, chunk_overlap):
        """Split text in overlapped chunks.

        This method executes the `rabbithole_splits_text` to split the incoming text in overlapped
        chunks of text. Other two hooks are available to edit the text before and after the split step.

        Parameters
        ----------
        text : str
            Content of the loaded file.
        chunk_size : int
            Number of characters in each document chunk.
        chunk_overlap : int
            Number of overlapping characters between consecutive chunks.

        Returns
        -------
        docs : List[Document]
            List of split Langchain `Document`.

        Notes
        -----
        The default behavior only executes the `rabbithole_splits_text` hook. `before_rabbithole_splits_text` and
        `after_rabbithole_splitted_text` hooks return the original input without any modification.

        See Also
        --------
        before_rabbithole_splits_text
        rabbithole_splits_text
        after_rabbithole_splitted_text

        """
        # do something on the text before it is split
        text = self.cat.mad_hatter.execute_hook(
            "before_rabbithole_splits_text", text
        )

        # split the documents using chunk_size and chunk_overlap
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\\n\\n", "\n\n", ".\\n", ".\n", "\\n", "\n", " ", ""],
        )
        # split text
        docs = text_splitter.split_documents(text)
        # remove short texts (page numbers, isolated words, etc.)
        # TODO: join each short chunk with previous one, instead of deleting them
        docs = list(filter(lambda d: len(d.page_content) > 10, docs))

        # do something on the text after it is split
        docs = self.cat.mad_hatter.execute_hook(
            "after_rabbithole_splitted_text", docs
        )

        return docs
