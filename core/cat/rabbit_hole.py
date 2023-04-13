import os
import time
import tempfile
import mimetypes
from typing import Union

from cat.utils import log
from langchain.text_splitter import RecursiveCharacterTextSplitter
from starlette.datastructures import UploadFile
from langchain.document_loaders import (
    PDFMinerLoader,
    UnstructuredFileLoader,
    UnstructuredMarkdownLoader,
)


class RabbitHole:
    def __init__(self):
        pass

    # This is not actually a class method, better to make a function or should it be decorated with @staticmethod?
    def ingest_file(
        self,
        ccat,  # Type declaration removed as it raise a circular import error
        file: Union[str, UploadFile],
        chunk_size: int = 400,
        chunk_overlap: int = 100,
    ):
        """
        Send a file down to the RabbitHole and load the file in the Cat's declarative memory.
        The file can either be ingested from the web GUI or using the Cat *send_file_in_rabbit_hole* method.
        :param ccat: instance of the CheshireCat object
        :param file: absolute path of the file or UploadFile if ingested from the GUI
        :param chunk_size: number of characters the text is split in
        :param chunk_overlap: number of overlapping characters between consecutive chunks
        """

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(dir=".", delete=False)
        temp_name = temp_file.name

        # Check type of incoming file.
        # It can be either UploadFile if coming from GUI or an absolute path if auto-ingested be the Cat
        if isinstance(file, UploadFile):
            # Get mime type of UploadFile
            content_type = file.content_type

            # Get filename
            filename = file.filename

            # Get file bytes
            file_bytes = file.file.read()

        elif isinstance(file, str):
            # Get mime type from file extension
            content_type = mimetypes.guess_type(file)[0]

            # Get filename
            filename = os.path.basename(file)

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

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\\n\\n", "\n\n", ".\\n", ".\n", "\\n", "\n", " ", ""],
        )
        docs = text_splitter.split_documents(text)

        log(f"Preparing to clean {len(docs)} text chunks")

        # remove short texts (page numbers, isolated words, etc.)
        docs = list(filter(lambda d: len(d.page_content) > 10, docs))

        log(f"Doing iterative summarization over {len(docs)} chunks")

        # iterative summarization
        final_summary, intermediate_summaries = ccat.get_summary_text(docs)

        # we store in memory both original text chunks, intermediate summaries and final summary
        docs = [final_summary] + intermediate_summaries + docs

        log(docs)

        log(f"Preparing to memorize {len(docs)} vectors")

        # classic embed
        for d, doc in enumerate(docs):
            _ = ccat.memory["documents"].add_texts(
                [doc.page_content],
                [
                    {
                        "source": filename,
                        "when": time.time(),
                        "text": doc.page_content,
                    }
                ],
            )
            log(f"Inserted into memory ({d + 1}/{len(docs)}):    {doc.page_content}")
            time.sleep(0.1)

        ccat.vector_store.save_vector_store("documents", ccat.memory["documents"])

        log("Done uploading")  # TODO: notify client
