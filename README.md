# 🐱 Cheshire-Cat (Stregatto)

## Customizable AI architecture

- language model agnostic (works with OpenAI, Cohere, HuggingFace models, custom)
- long term memory
- can use external tools (APIs, other models)
- can ingest documents (.pdf, .txt)
- 100% dockerized
- extendible via plugins

<p align="center">
    <img align="center" src=cheshire-cat.jpeg width=400px alt="Wikipedia picture of the Cheshire Cat">
</p>

```
"Would you tell me, please, which way I ought to go from here?"
"That depends a good deal on where you want to get to," said the Cat.
"I don't much care where--" said Alice.
"Then it doesn't matter which way you go," said the Cat.

(Alice's Adventures in Wonderland - Lewis Carroll)

```


## Quickstart

You just need `docker` and `docker-compose` installed on your system.

Clone the repo and cd into it. Create a `.env` file containing:

```
OPENAI_KEY=<your-openai-key>
```

### Without Docker

```
cd ./web
virtualenv env
source ./env/bin/activate
pip install -r requirements.txt
pip install uvicorn[standard] gunicorn langchain beautifulsoup4 openai
uvicorn cat.main:cheshire_cat_api --host 127.0.0.1 --port 1865 # run the backend

cd ./frontend
npm install
npm run build
npm run dev # run the frontend
```

- Chat with the Cheshire Cat on `localhost:3000`.
- You can also interact via REST API and try out the endpoints on `localhost:1865/docs`

You need to run the 2 set of commands in 2 different shell windows as they are 2 different web servers.  
The installation part is required just once.

### Docker

After that you can run:

```bash
docker-compose up
```

The first time (only) it will take several minutes, as the images occupy a few GBs.

- Chat with the Cheshire Cat on `localhost:3000`.
- You can also interact via REST API and try out the endpoints on `localhost:1865/docs`

When you finish, remember to CTRL+c in the terminal and
```
docker-compose down
```

## Roadmap

- Coming soon


## Contributing

Your contribution is **greatly appreciated**. Things you can do to help the project:
- try out the Cat
- read, comment and open issues
- make a pull request (if it contains lots of code, please discuss it beforehand opening a issue)
- making tutorials and docs
- sharing on social media

Don't forget to give the project a star! Thanks again!
