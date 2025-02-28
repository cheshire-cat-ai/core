FROM python:3.10.11-slim-bullseye

### ENVIRONMENT VARIABLES ###
ENV PYTHONUNBUFFERED=1
ENV WATCHFILES_FORCE_POLLING=true

### SYSTEM SETUP ###
RUN apt-get -y update && apt-get install -y curl build-essential fastjar libmagic-mgc libmagic1 mime-support && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

### ADMIN (static build) ###
WORKDIR /admin
RUN curl -sL https://github.com/cheshire-cat-ai/admin-vue/releases/download/Admin/release.zip | jar -xv

### PREPARE BUILD WITH NECESSARY FILES AND FOLDERS ###
COPY ./pyproject.toml /app/pyproject.toml

### INSTALL PYTHON DEPENDENCIES (Core) ###
WORKDIR /app
RUN pip install -U pip && \
    pip install --no-cache-dir . &&\
    python3 -c "import nltk; nltk.download('punkt');nltk.download('averaged_perceptron_tagger');import tiktoken;tiktoken.get_encoding('cl100k_base')"

### COPY CAT CODE INSIDE THE CONTAINER (so it can be run standalone) ###
COPY ./cat /app/cat

### INSTALL PYTHON DEPENDENCIES (Plugins) ###
COPY ./install_plugin_dependencies.py /app/install_plugin_dependencies.py
RUN python3 install_plugin_dependencies.py

### FINISH ###
CMD python3 -m cat.main
