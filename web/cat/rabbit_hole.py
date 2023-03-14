
import tempfile
import os
import time

from fastapi import UploadFile
from langchain.document_loaders import PDFMinerLoader, UnstructuredFileLoader

from cat.utils import log


def ingest_file(file: UploadFile, ccat):

    # read file content
    #content = file.read()
    
    temp_name = next(tempfile._get_candidate_names())
    
    # Open file in binary write mode
    binary_file = open(temp_name, "wb")
    
    # Write bytes to file
    binary_file.write(file.file.read())
    
    # Close file
    binary_file.flush()
    binary_file.close()

    if file.content_type == 'text/plain':
        # content = str(content, 'utf-8')
        # TODO: use langchain splitters
        # TODO: also use an overlap window between docs and summarizations
        # docs = content.split('\n\n')
        loader = UnstructuredFileLoader(f"./{temp_name}")        
        data = loader.load()
        
    if file.content_type == 'application/pdf':
        # Manage the byte stram
        loader = PDFMinerLoader(f"./{temp_name}")
        data = loader.load()
        
    # delete file
    os.remove(f"./{temp_name}")
    log(len(data))
    
    docs = []
    # classic embed
    for doc in data:
        # log(dir(doc)) #.split_text('\n')
        a = doc.dict()
        docs = docs + [row.strip() for row in a['page_content'].split('\n')]
        
    log(f'Preparing to clean {len(docs)} vectors')

    # remove duplicates
    docs = list(set(docs))
    if '' in docs:
        docs.remove('')
    log(f'Preparing to memorize {len(docs)} vectors')

    # classic embed
    for doc in docs:
        id = ccat.declarative_memory.add_texts(
            [doc],
            [{
                'source' : file.filename,
                'when': time.time(),
                'text': doc,
            }]
        )
        log(f'Inserted into memory:\n{doc}')
        time.sleep(0.3)

    # TODO: HyDE embed    


