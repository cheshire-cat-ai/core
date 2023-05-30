
FROM tiangolo/uvicorn-gunicorn:python3.10

### CORE ###

COPY ./pyproject.toml pyproject.toml
COPY ./cat/plugins ./cat/plugins
COPY ./install_plugin_dependencies.py install_plugin_dependencies.py
WORKDIR /admin

RUN pip install -U pip && \
    pip install --no-cache-dir /app &&\
    python3 /app/install_plugin_dependencies.py &&\
### ADMIN (static build) ###
    curl -sL https://github.com/pieroit/cheshire-cat-admin/archive/main.tar.gz | tar xz -C /admin --strip-components=1 &&\
    curl -fsSLO --compressed "https://nodejs.org/dist/v18.16.0/node-v18.16.0-linux-x64.tar.xz" &&\
    tar -xJf node-v18.16.0-linux-x64.tar.xz -C /usr/local --strip-components=1 --no-same-owner &&\
    rm node-v18.16.0-linux-x64.tar.xz &&\
    ln -s /usr/local/bin/node /usr/local/bin/nodejs &&\
    npm install &&\
    npm run build

### ADMIN (static build) ###

### FINISH ###
WORKDIR /app
# ready to go (docker-compose up)

