
FROM python:3.10.11-slim-bullseye

ARG USER_ONBUILD=cat
ARG UID_ONBUILD=1001
ARG GROUP_ONBUILD=cat
ARG GID_ONBUILD=1001

### SYSTEM SETUP ###
RUN apt-get -y update && apt-get install -y curl build-essential fastjar libmagic-mgc libmagic1 mime-support && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

### ADMIN (static build) ###
WORKDIR /admin
RUN curl -sL https://github.com/cheshire-cat-ai/admin-vue/releases/download/Admin/develop.zip | jar -xv

### PREPARE BUILD WITH NECESSARY FILES AND FOLDERS ###
COPY ./pyproject.toml /app/pyproject.toml

### INSTALL PYTHON DEPENDENCIES (Core) ###
WORKDIR /app
RUN pip install -U pip && \
    pip install --no-cache-dir . &&\
    python3 -c "import nltk; nltk.download('punkt');nltk.download('averaged_perceptron_tagger')"

### ADD USER ###
RUN groupadd -g ${GID_ONBUILD} ${GROUP_ONBUILD} && \
   useradd -m -u ${UID_ONBUILD} -g ${GROUP_ONBUILD} ${USER_ONBUILD} \
   && chown -R ${GROUP_ONBUILD}:${USER_ONBUILD} /app

USER ${GROUP_ONBUILD}:${USER_ONBUILD}

### CREATE HOME LOCAL BIN FOLDER IF NOT EXIST ###
RUN mkdir -p /home/${USER_ONBUILD}/.local/bin

### ADD HOME LOCAL BIN FOLDER TO THE PATH ###
ENV PATH="/home/${USER_ONBUILD}/.local/bin:${PATH}"

### COPY CAT CODE INSIDE THE CONTAINER (so it can be run standalone) ###
COPY ./cat /app/cat

### INSTALL PYTHON DEPENDENCIES (Plugins) ###
COPY ./install_plugin_dependencies.py /app/install_plugin_dependencies.py
RUN python3 install_plugin_dependencies.py

### FINISH ###
CMD python3 -m cat.main
