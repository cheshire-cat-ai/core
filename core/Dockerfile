
FROM tiangolo/uvicorn-gunicorn:python3.10

RUN apt-get update -y


### CORE ###

#RUN apt-get install -y poppler-utils tesseract-ocr libreoffice ### needed form unstructured?

COPY ./pyproject.toml pyproject.toml
RUN pip install -U pip
RUN pip install --no-cache-dir ./

COPY ./cat/plugins ./cat/plugins
COPY ./install_plugin_dependencies.py install_plugin_dependencies.py

RUN python3 install_plugin_dependencies.py


### ADMIN (static build) ###

# install node
WORKDIR /
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# clone admin sources
RUN git clone https://github.com/pieroit/cheshire-cat-admin.git admin
WORKDIR /admin
# install and build
RUN npm install && npm run build


### FINISH ###
WORKDIR /app
# ready to go (docker-compose up)

