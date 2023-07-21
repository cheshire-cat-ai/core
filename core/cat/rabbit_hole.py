import os
import time
import json
import tempfile
import mimetypes
from typing import List, Union

from cat.log import log
from starlette.datastructures import UploadFile
from fastapi import HTTPException
from langchain.document_loaders import (
    PDFMinerLoader,
    UnstructuredURLLoader,
    UnstructuredFileLoader,
    UnstructuredMarkdownLoader,
)
from langchain.docstore.document import Document
from qdrant_client.http import models


class RabbitHole:
    """

    """

    def __init__(self, cat):
        self.cat = cat

    @staticmethod
    def check_mime_type(file: UploadFile, admitted_types: list):

        # Get file mime type
        content_type = mimetypes.guess_type(file.filename)[0]
        log(f"Uploaded {content_type} down the rabbit hole", "INFO")

        # check if MIME type of uploaded file is supported
        if content_type not in admitted_types:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": f'MIME type {content_type} not supported. Admitted types: {" - ".join(admitted_types)}'}
            )

    def ingest_memory(self, file: UploadFile):

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(dir="/tmp/", delete=False)
        temp_name = temp_file.name

        # Get file bytes
        file_bytes = file.file.read()

        # Save in temporary file
        with open(temp_name, "wb") as temp_binary_file:
            temp_binary_file.write(file_bytes)

        # Recover the file as dict
        with open(temp_name, "rb") as memories_file:
            content = memories_file.read().decode("latin1")
            memories = json.loads(content, strict=False)

        log(file_bytes, "ERROR")

        # Remove temp file
        os.remove(temp_name)

        # Check the embedder used for the uploaded memories is the same the Cat is using now
        upload_embedder = memories["embedder"]
        cat_embedder = str(self.cat.embedder.__class__.__name__)

        if upload_embedder != cat_embedder:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": f'Embedder mismatch: uploaded file embedder {upload_embedder} is different from {ccat.embedder}'}
            )

        # Get Declarative memories in file
        declarative_memories = memories["collections"]["declarative"]

        # Store data to upload the memories in batch
        ids = [i["id"] for i in declarative_memories]
        payloads = [{
            "page_content": p["page_content"],
            "metadata": p["metadata"]
        } for p in declarative_memories]
        vectors = [v["vector"] for v in declarative_memories]

        log(f"Preparing to load {len(vectors)} vector memories", "ERROR")

        # Check embedding size is correct
        embedder_size = self.cat.memory.vectors.embedder_size
        len_mismatch = [len(v) == embedder_size for v in vectors]

        if not any(len_mismatch):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": f'Embedding size mismatch: vectors length should be {embedder_size}'}
            )

        # Upsert memories in batch mode
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
            chunk_overlap: int = 100,
            summary: bool = False,
    ):
        """Load a file in the Cat's declarative memory.

        The method splits and converts the file in Langchain `Document`. Then, it stores the `Document` in the Cat's
        memory. Optionally, the document can be summarized and summaries are saved along with the original
        content.

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
        rabbithole_summarizes_documents
        """

        # split file into a list of docs
        docs = self.file_to_docs(
            file=file, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # get summaries if summarization is requested
        if summary:
            summaries = self.cat.mad_hatter.execute_hook(
                "rabbithole_summarizes_documents", docs
            )
            docs = summaries + docs

        # store in memory
        if isinstance(file, str):
            filename = file
        else:
            filename = file.filename
        self.store_documents(docs=docs, source=filename)

    def ingest_url(
            self,
            url: str,
            chunk_size: int = 400,
            chunk_overlap: int = 100,
            summary: bool = False,
    ):
        """Load a webpage in the Cat's declarative memory.

        The method splits and converts a `.html` page to Langchain `Document`. Then, it stores the `Document` in
        the Cat's memory. Optionally, the document can be summarized and summaries are saved along with the
        original content.

        Parameters
        ----------
        url : str
            Url to the webpage.
        chunk_size : int
            Number of characters in each document chunk.
        chunk_overlap : int
            Number of overlapping characters between consecutive chunks.

        See Also
        ----------
        rabbithole_summarizes_documents

        """

        # get website content and split into a list of docs
        docs = self.url_to_docs(
            url=url, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # get summaries if summarization requested
        if summary:
            summaries = self.cat.mad_hatter.execute_hook(
                "rabbithole_summarizes_documents", docs
            )
            docs = summaries + docs

        # store docs in memory
        self.store_documents(docs=docs, source=url)

    def url_to_docs(
            self,
            url: str,
            chunk_size: int = 400,
            chunk_overlap: int = 100,
    ) -> List[Document]:
        """Converts an url to Langchain `Document`.

        The method loads and splits an url content in overlapped chunks of text.
        The content is then converted to Langchain `Document`.

        Parameters
        ----------
        url : str
            Url to the webpage.
        chunk_size : int
            Number of characters in each document chunk.
        chunk_overlap : int
            Number of overlapping characters between consecutive chunks.

        Returns
        -------
        docs : List[Document]
            List of Langchain `Document` of chunked text.

        """

        # load text content of the website
        loader = UnstructuredURLLoader(urls=[url])
        text = loader.load()

        docs = self.split_text(text, chunk_size, chunk_overlap)

        return docs

    def file_to_docs(
            self,
            file: Union[str, UploadFile],
            chunk_size: int = 400,
            chunk_overlap: int = 100,
    ) -> List[Document]:

        """Load and convert files to Langchain `Document`.

        This method takes a file either from a Python script or from the `/rabbithole/` endpoint.
        Hence, it loads it in memory and splits it in overlapped chunks of text.

        Parameters
        ----------
        file : str, UploadFile
            The file can be either a string path if loaded programmatically or a FastAPI `UploadFile` if coming from
            the `/rabbithole/` endpoint.
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
        Currently supported formats are `.txt`, `.pdf` and `.md`.
        """

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(dir="/tmp/", delete=False)
        temp_name = temp_file.name

        # Check type of incoming file.
        # It can be either UploadFile if coming from GUI
        #   or an absolute path if auto-ingested be the Cat
        if isinstance(file, UploadFile):
            # Get mime type of UploadFile
            # content_type = file.content_type
            content_type = mimetypes.guess_type(file.filename)[0]

            # Get file bytes
            file_bytes = file.file.read()

        elif isinstance(file, str):
            # Get mime type from file extension
            content_type = mimetypes.guess_type(file)[0]

            # Get file bytes
            with open(file, "rb") as f:
                file_bytes = f.read()
        else:
            raise ValueError(f"{type(file)} is not a valid type.")

        # Open temp file in binary write mode
        with open(temp_name, "wb") as temp_binary_file:
            # Write bytes to file
            temp_binary_file.write(file_bytes)

        # decide loader
        if content_type == "text/plain":
            loader = UnstructuredFileLoader(temp_name)
        elif content_type == "text/markdown":
            loader = UnstructuredMarkdownLoader(temp_name)
        elif content_type == "application/pdf":
            loader = PDFMinerLoader(temp_name)
        else:
            raise Exception("MIME type not supported for upload")

        # extract text from file
        text = loader.load()
        # delete tmp file
        os.remove(temp_name)

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

        log(f"Preparing to memorize {len(docs)} vectors")

        # classic embed
        for d, doc in enumerate(docs):
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

                # log(f"Inserted into memory({inserting_info})", "INFO")
                print(f"Inserted into memory({inserting_info})")
            else:
                log(f"Skipped memory insertion of empty doc ({inserting_info})", "INFO")

            # wait a little to avoid APIs rate limit errors
            time.sleep(0.1)

        # notify client
        finished_reading_message = f"Finished reading {source}, " \
                                   f"I made {len(docs)} thoughts on it."
        self.cat.web_socket_notifications.append(
            {
                "error": False,
                "type": "notification",
                "content": finished_reading_message,
                "why": {},
            }
        )

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
        docs = self.cat.mad_hatter.execute_hook(
            "rabbithole_splits_text", text, chunk_size, chunk_overlap
        )

        # do something on the text after it is split
        docs = self.cat.mad_hatter.execute_hook(
            "after_rabbithole_splitted_text", docs
        )

        return docs
