# TODO: better start with a cuda image? Dunno
FROM tiangolo/uvicorn-gunicorn:python3.9

RUN apt-get update -y
#RUN apt-get install -y poppler-utils tesseract-ocr libreoffice ### needed form unstructured?

RUN pip install --upgrade --no-cache-dir \
    fastapi==0.92.0 \
    websockets==10.4 \
    python-multipart==0.0.6 \
    pandas==1.5.3 \
    scikit-learn==1.2.1 \
    torch==1.13.1 \
    torchvision==0.14.1 \
    transformers==4.26.1 \ 
    langchain==0.0.98 \
    unstructured[local-inference]==0.5.3 \
    qdrant_client==1.0.1 \
    openai==0.27.0
