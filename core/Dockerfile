
FROM nikolaik/python-nodejs:python3.11-nodejs20

### PREPARE BUILD WITH NECESSARY FILES AND FOLDERS ###
RUN mkdir -p /app && mkdir -p /admin
COPY ./pyproject.toml /app/pyproject.toml
COPY ./cat/plugins /app/cat/plugins
COPY ./install_plugin_dependencies.py /app/install_plugin_dependencies.py

### SYSTEM SETUP ###
RUN apt-get -y update && apt-get install -y curl build-essential xz-utils libmagic-mgc libmagic1 mime-support && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

### ADMIN (static build) ###
WORKDIR /admin
RUN curl -sL https://github.com/cheshire-cat-ai/admin-vue/archive/main.tar.gz | tar xz -C /admin --strip-components=1 &&\
    npm install &&\
    npm run build

### INSTALL PYTHON DEPENDENCIES (Core and Plugins) ###
WORKDIR /app
RUN pip install -U pip && \
    pip install --no-cache-dir ./ &&\
    python3 install_plugin_dependencies.py


### FINISH ###
# ready to go (docker-compose up)

