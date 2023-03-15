import os
import time
import tempfile
from typing import List

from fastapi import UploadFile
from cat.utils import log
from langchain.document_loaders import PDFMinerLoader, UnstructuredFileLoader


def ingest_file(file: UploadFile, ccat):
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(dir=".", delete=False)
    temp_name = temp_file.name

    # Open temp file in binary write mode
    with open(temp_name, "wb") as temp_binary_file:
        # Write bytes to file
        temp_binary_file.write(file.file.read())

    if file.content_type == "text/plain":
        # content = str(content, 'utf-8')
        # TODO: use langchain splitters
        # TODO: also use an overlap window between docs and summarizations
        # docs = content.split('\n\n')
        loader = UnstructuredFileLoader(temp_name)
        data = loader.load()

    if file.content_type == "application/pdf":
        # Manage the byte stram
        loader = PDFMinerLoader(temp_name)
        data = loader.load()

    # delete file
    os.remove(temp_name)
    log(len(data))

    docs: List = []
    # split content
    for doc in data:
        docs = docs + [row.strip() for row in doc.page_content.split("\n\n")]

    log(f"Preparing to clean {len(docs)} vectors")

    # remove duplicates
    docs = list(set(docs))
    if "" in docs:
        docs.remove("")
    log(f"Preparing to memorize {len(docs)} vectors")

    # classic embed
    for d, doc in enumerate(docs):
        _ = ccat.declarative_memory.add_texts(
            [doc],
            [
                {
                    "source": file.filename,
                    "when": time.time(),
                    "text": doc,
                }
            ],
        )
        log(f"Inserted into memory ({d+1}/{len(docs)}):    {doc}")
        time.sleep(0.3)

    log("Done uploading")  # TODO: notify client

    # TODO: HyDE embed
