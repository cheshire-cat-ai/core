# TODO: better start with a cuda image? Dunno
FROM tiangolo/uvicorn-gunicorn:python3.10

RUN apt-get update -y
#RUN apt-get install -y poppler-utils tesseract-ocr libreoffice ### needed form unstructured?

COPY ./requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt
