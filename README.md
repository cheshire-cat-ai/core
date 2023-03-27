<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="">
    <img src="https://cdn-icons-png.flaticon.com/512/3394/3394293.png" alt="Logo" width="80" height="80">
  </a>
  <h2 align="center">Cheshire-Cat (Stregatto)</h2>
  <h4 align="center">
    Customizable AI architecture
  </h4>
</div>

## What is this?

If you want to build a custom AI on top of a language model, the Cat can help you:

- Language model agnostic (works with OpenAI, Cohere, HuggingFace models, custom)
- Long term memory
- Can use external tools (APIs, custom python code, other models)
- Can ingest documents (.pdf, .txt)
- Extendible via plugins
- 100% [dockerized](https://docs.docker.com/get-docker/)

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

### Docker

After that you can run:

```bash
docker-compose up
```

The first time (only) it will take several minutes, as the images occupy a few GBs.

- Chat with the Cheshire Cat on `localhost:3000`.
- You can also interact via REST API and try out the endpoints on `localhost:1865/docs`

When you're done, remember to CTRL+c in the terminal and
```
docker-compose down
```

### [Advanced] Manual way

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

- QA / tests
- docs and tutorials
- online demo
- voice interface
- more plugins shipped by default
- (surprise!!!) PURR

## Contributing

If you have a suggestion that would make this better, open an issue and we can reason about it.
If you want to contribute code, fork the repo and create a pull request.

1. Try out the Cat
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request ((if it contains lots of code, please discuss it beforehand opening a issue))

You can start simply by:
- Making tutorials and docs
- Sharing on social media

Don't forget to give the project a star!⭐ Thanks again!🙏

<p align="right">(<a href="#readme-top">back to top</a>)</p>
