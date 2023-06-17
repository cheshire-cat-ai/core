
FROM python:3.10.11-slim-bullseye

### PREPARE BUILD WITH NECESSARY FILES AND FOLDERS ###
RUN mkdir -p /app && mkdir -p /admin
COPY ./pyproject.toml /app/pyproject.toml
COPY ./cat/plugins /app/cat/plugins
COPY ./install_plugin_dependencies.py /app/install_plugin_dependencies.py

### SYSTEM SETUP ###
RUN apt-get -y update && apt-get install -y curl build-essential xz-utils libmagic-mgc libmagic1 mime-support && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

### INSTALL NODEJS ###
RUN NODEARCH= && dpkgArch="$(dpkg --print-architecture)" &&\
    case "${dpkgArch##*-}" in \
      amd64) NODEARCH='x64';; \
      ppc64el) NODEARCH='ppc64le';; \
      s390x) NODEARCH='s390x';; \
      arm64) NODEARCH='arm64';; \
      armhf) NODEARCH='armv7l';; \
      i386) NODEARCH='x86';; \
      *) echo "unsupported architecture"; exit 1 ;;\
    esac &&\
    curl -fsSLO --compressed "https://nodejs.org/dist/v18.16.0/node-v18.16.0-linux-${NODEARCH}.tar.xz" &&\
    tar -xJf node-v18.16.0-linux-${NODEARCH}.tar.xz -C /usr/local --strip-components=1 --no-same-owner &&\
    rm node-v18.16.0-linux-${NODEARCH}.tar.xz &&\
    ln -s /usr/local/bin/node /usr/local/bin/nodejs

### ADMIN (static build) ###
WORKDIR /admin
RUN curl -sL https://github.com/cheshire-cat-ai/admin-vue/archive/main.tar.gz | tar xz -C /admin --strip-components=1 &&\
    npm install &&\
    npm run build

### INSTALL PYTHON DEPENDENCIES (Core and Plugins) ###
WORKDIR /app
RUN pip install -U pip && \
    pip install --no-cache-dir ./ &&\
    python3 -c "import nltk; nltk.download('punkt')" &&\
    python3 install_plugin_dependencies.py


### FINISH ###
# ready to go (docker-compose up)

