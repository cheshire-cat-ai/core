# :rocket: Getting started

## Download
Clone the repository on your machine:

```bash
# Clone the repository
git clone https://github.com/pieroit/cheshire-cat.git
```

## Install
To run the Cheshire Cat, you need to have `docker` ([instructions](https://docs.docker.com/engine/install/)) and `docker-compose` ([instructions](https://docs.docker.com/compose/install/)) installed on your system.

- Create and API key on the language model provider website  
- Make a copy of the `.env.example` file and rename it `.env`
- Start the app with `docker-compose up` inside the repository
- Open the app in your browser at `localhost:3000`
- Configure a LLM in the `Settings` tab and paste you API key
- Start chatting

You can also interact via REST API and try out the endpoints on `localhost:1865/docs`

The first time you run the `docker-compose up` command it will take several minutes as docker images occupy some GBs.

## Quickstart
Here is an example of a quick setup running the `gpt3.5-turbo` OpenAI [model](https://platform.openai.com/docs/models/gpt-3-5).  

Create an API key with `+ Create new secret key` in your OpenAI [personal account](https://platform.openai.com/account/api-keys), then:

### CLI setup
=== "Linux & Mac"

    ```bash
    # Open the cloned repository
    cd cheshire-cat
    
    # Create the .env file
    cp .env.example .env
    
    # Run docker containers
    docker-compose up
    ```
=== "Windows"
    
    ```bash
    # Open the cloned repository
    cd cheshire-cat
    
    # Create the .env file
    copy .env.example .env
    
    # Run docker containers
    docker-compose up
    ```

### GUI setup   

![type:video](../assets/vid/setup.mp4)

    
When you're done using the Cat, remember to CTRL+c in the terminal and `docker-compose down`.

## Update
As the project is still a work in progress, if you want to update it run the following:
```bash
# Open the cloned repository
cd cheshire-cat

# Pull from the main remote repository
git pull

# Build again the docker containers
docker-compose build --no-cache

# Remove dangling images (optional)
docker rmi -f $(docker images -f "dangling=true" -q)

# Run docker containers
docker-compose up
```
