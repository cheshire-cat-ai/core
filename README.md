<a name="readme-top"></a>

# 🐱 Cheshire-Cat (Stregatto)

## Customizable AI architecture

- Language model agnostic (works with OpenAI, Cohere, HuggingFace models, custom)
- Long term memory
- Can use external tools (APIs, other models)
- Can ingest documents (.pdf, .txt)
- 100% [dockerized](https://www.docker.com/)
- Extendible via plugins

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap 

- Coming soon...


## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

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



