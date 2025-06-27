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
RUN curl -sL https://github.com/cheshire-cat-ai/admin-vue/releases/download/Admin/develop.zip | jar -xv

WORKDIR /app

### PREPARE BUILD WITH NECESSARY FILES AND FOLDERS ###
COPY ./ /app/
RUN rm -fr .venv 
# TODO venv should stay in another folder, otherwise conflicts with local venv

### INSTALL PYTHON DEPENDENCIES (Core) ###
RUN pip install uv && uv sync
RUN uv run python3 -c "import nltk; nltk.download('punkt');nltk.download('averaged_perceptron_tagger');import tiktoken;tiktoken.get_encoding('cl100k_base')"
# RUN uv run python3 install_plugin_dependencies.py TODO: use uv inside the script

### FINISH ###
CMD python3 -m cat.main
