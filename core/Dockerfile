
FROM python:3.10.11-slim-bullseye

### CORE ###

RUN mkdir -p /app && mkdir -p /admin
COPY ./pyproject.toml /app/pyproject.toml
COPY ./cat/plugins /app/cat/plugins
COPY ./install_plugin_dependencies.py /app/install_plugin_dependencies.py
WORKDIR /admin

RUN apt-get -y update && apt-get install -y curl xz-utils libmagic-mgc libmagic1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* &&\
    NODEARCH= && dpkgArch="$(dpkg --print-architecture)" &&\
    case "${dpkgArch##*-}" in \
      amd64) NODEARCH='x64';; \
      ppc64el) NODEARCH='ppc64le';; \
      s390x) NODEARCH='s390x';; \
      arm64) NODEARCH='arm64';; \
      armhf) NODEARCH='armv7l';; \
      i386) NODEARCH='x86';; \
      *) echo "unsupported architecture"; exit 1 ;;\
    esac &&\
    pip install -U pip && \
    pip install --no-cache-dir /app/ &&\
    python3 /app/install_plugin_dependencies.py &&\
### ADMIN (static build) ###
    curl -sL https://github.com/pieroit/cheshire-cat-admin/archive/main.tar.gz | tar xz -C /admin --strip-components=1 &&\
    curl -fsSLO --compressed "https://nodejs.org/dist/v18.16.0/node-v18.16.0-linux-${NODEARCH}.tar.xz" &&\
    tar -xJf node-v18.16.0-linux-${NODEARCH}.tar.xz -C /usr/local --strip-components=1 --no-same-owner &&\
    rm node-v18.16.0-linux-${NODEARCH}.tar.xz &&\
    ln -s /usr/local/bin/node /usr/local/bin/nodejs &&\
    npm install &&\
    npm run build

### ADMIN (static build) ###

### FINISH ###
WORKDIR /app
# ready to go (docker-compose up)

