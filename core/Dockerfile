
FROM python:3.10.11-slim-bullseye

### PREPARE BUILD WITH NECESSARY FILES AND FOLDERS ###
RUN mkdir -p /app && mkdir -p /admin
COPY ./pyproject.toml /app/pyproject.toml
COPY ./cat/plugins /app/cat/plugins
COPY ./install_plugin_dependencies.py /app/install_plugin_dependencies.py

### SYSTEM SETUP ###
RUN apt-get -y update && apt-get install -y curl build-essential fastjar libmagic-mgc libmagic1 mime-support && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

### ADMIN (static build) ###
WORKDIR /admin
RUN curl -sL https://github.com/cheshire-cat-ai/admin-vue/releases/download/Admin/release.zip | jar -xv

### INSTALL PYTHON DEPENDENCIES (Core and Plugins) ###
WORKDIR /app
RUN pip install -U pip && \
    pip install --no-cache-dir . &&\
    python3 -c "import nltk; nltk.download('punkt');nltk.download('averaged_perceptron_tagger')" &&\
    python3 install_plugin_dependencies.py


### FINISH ###
# ready to go (docker-compose up)

