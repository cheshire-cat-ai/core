import os
import time
import tempfile
from typing import List, Union

from cat.log import log
from cat.utils import guess_mimetype_from_filename
from starlette.datastructures import UploadFile
from langchain.document_loaders import (
    PDFMinerLoader,
    UnstructuredURLLoader,
    UnstructuredFileLoader,
    UnstructuredMarkdownLoader,
)
from langchain.docstore.document import Document


class RabbitHole:
    def __init__(self, cat):
        self.cat = cat

    def ingest_file(
        self,
        file: Union[str, UploadFile],
        chunk_size: int = 400,
        chunk_overlap: int = 100,
    ):
        """
        Load a given file in the Cat's memory.

        :param file: absolute path of the file or UploadFile
            if ingested from the GUI
        :param chunk_size: number of characters the text is split in
        :param chunk_overlap: number of overlapping characters
            between consecutive chunks
        """

        # split file into a list of docs
        docs = self.file_to_docs(
            file=file, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # get summaries
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
    ):
        """
        Load a given website in the Cat's memory.
        :param url: URL of the website to which you want to save the content
        :param chunk_size: number of characters the text is split in
        :param chunk_overlap: number of overlapping characters
            between consecutive chunks
        """

        # get website content and split into a list of docs
        docs = self.url_to_docs(
            url=url, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # get summaries
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
        """
        Scrape website content and chunk it to a list of Documents.
        :param url: URL of the website to which you want to save the content
        :param chunk_size: number of characters the text is split in
        :param chunk_overlap: number of overlapping characters
            between consecutive chunks
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
        """
        Parse a file and chunk it to a list of Documents.
        The file can either be ingested from the web GUI, rest API
            or using the *cat.rabbit_hole.send_file_in_rabbit_hole* method.
        :param file: absolute path of the file or UploadFile
            if ingested from the GUI
        :param chunk_size: number of characters
            the text is split in
        :param chunk_overlap: number of overlapping characters
            between consecutive chunks
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
            content_type = guess_mimetype_from_filename(file.filename)

            # Get file bytes
            file_bytes = file.file.read()

        elif isinstance(file, str):
            # Get mime type from file extension
            content_type = guess_mimetype_from_filename(file)

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
        """
        Load a list of Documents in the Cat's declarative memory.
        :param ccat: reference to the cat instance
        :param docs: a list of documents to store in memory
        :param source: a string representing the source,
            either the file name or the website URL
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

                #log(f"Inserted into memory({inserting_info})", "INFO")
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
        # do something on the text before it is splitted
        text = self.cat.mad_hatter.execute_hook(
            "before_rabbithole_splits_text", text
        )

        # split the documents using chunk_size and chunk_overlap
        docs = self.cat.mad_hatter.execute_hook(
            "rabbithole_splits_text", text, chunk_size, chunk_overlap
        )

        # do something on the text after it is splitted
        docs = self.cat.mad_hatter.execute_hook(
            "after_rabbithole_splitted_text", docs
        )

        return docs
