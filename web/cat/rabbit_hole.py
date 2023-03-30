import os
import tempfile
import time
from typing import List

from langchain.document_loaders import PDFMinerLoader, UnstructuredFileLoader, UnstructuredMarkdownLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import UploadFile

from cat.looking_glass.cheshire_cat import CheshireCat
from cat.utils import log


def ingest_file(ccat: CheshireCat, file: UploadFile, chunk_size: int = 400, chunk_overlap : int = 100):
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(dir=".", delete=False)
    temp_name = temp_file.name

    # Open temp file in binary write mode
    with open(temp_name, "wb") as temp_binary_file:
        # Write bytes to file
        temp_binary_file.write(file.file.read())

    # decide loader
    if file.content_type == "text/plain":
        loader = UnstructuredFileLoader(temp_name)
    elif file.content_type == "text/markdown":
        loader = UnstructuredMarkdownLoader(temp_name)  
    elif file.content_type == "application/pdf":
        loader = PDFMinerLoader(temp_name)
    else:
        raise Exception('MIME type not supported for upload')
    
    # extract text from file
    text = loader.load()

    # delete tmp file
    os.remove(temp_name)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\\n\\n", "\n\n", ".\\n", ".\n", "\\n", "\n", " ", ""]
    )
    docs = text_splitter.split_documents(text)

    log(f"Preparing to clean {len(docs)} text chunks")


    # remove short texts (page numbers, isolated words, etc.)
    docs = list(filter(lambda d: len(d.page_content) > 10, docs))


    log(f"Preparing to memorize {len(docs)} vectors")


    # TODO: hierarchical summarization
    # example: pass data to cat to get summary
    # summary = ccat.get_summary_text(data)


    # classic embed
    for d, doc in enumerate(docs):
        _ = ccat.memory["documents"].add_texts(
            [doc.page_content],
            [
                {
                    "source": file.filename,
                    "when": time.time(),
                    "text": doc.page_content,
                }
            ],
        )
        log(f"Inserted into memory ({d+1}/{len(docs)}):    {doc.page_content}")
        time.sleep(0.1)

    ccat.vector_store.save_vector_store("documents", ccat.memory["documents"])

    log("Done uploading")  # TODO: notify client

