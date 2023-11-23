<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h2>Cheshire-Cat (Stregatto)</h2>
<br/>
  <a href="https://github.com/cheshire-cat-ai/core">
  <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/cheshire-cat-ai/core?style=social">
</a>
  <a href="https://discord.gg/bHX5sNFCYU">
        <img src="https://img.shields.io/discord/1092359754917089350?logo=discord"
            alt="chat on Discord"></a>
  <a href="https://github.com/cheshire-cat-ai/core/issues">
  <img alt="GitHub issues" src="https://img.shields.io/github/issues/cheshire-cat-ai/core">
  </a>
  <a href="https://github.com/cheshire-cat-ai/core/tags">
  <img alt="GitHub tag (with filter)" src="https://img.shields.io/github/v/tag/cheshire-cat-ai/core">
  </a>
  <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/cheshire-cat-ai/core">

  <br/>
  <video src="https://github.com/cheshire-cat-ai/core/assets/6328377/7bc4acff-34bf-4b8a-be61-4d8967fbd60f"></video>
</div>

## Production ready AI assistant framework

The Cheshire Cat is a framework to build custom AIs on top of any language model. 
If you ever used systems like WordPress or Django to build web apps, imagine the Cat as a similar tool, but specific for AI.

## Quickstart

To make Cheshire Cat run on your machine, you just need [`docker`](https://docs.docker.com/get-docker/) installed:

```bash
docker run --rm -it -p 1865:80 ghcr.io/cheshire-cat-ai/core:latest
```
- Chat with the Cheshire Cat on [localhost:1865/admin](http://localhost:1865/admin).
- You can also interact via REST API and try out the endpoints on [localhost:1865/docs](http://localhost:1865/docs)

As a first thing, the Cat will ask you to configure your favourite language model.
It can be done directly via the interface in the Settings page (top right in the admin).

Enjoy the Cat!

## Docs and Resources

- [Official Documentation](https://cheshire-cat-ai.github.io/docs/)
- [Discord Server](https://discord.gg/bHX5sNFCYU)
- [Website](https://cheshirecat.ai/)
- [YouTube tutorial - How to install](https://youtu.be/Rvx19TZBCrw)
- [Tutorial - Write your first plugin](https://cheshirecat.ai/write-your-first-plugin/)

## Why use the Cat

- 🌍 Supports any language model (works with OpenAI chatGPT, LLAMA2, HuggingFace models, custom)
- 🐘 Remembers conversations and documents and uses them in conversation
- 🚀 Extensible via plugins (AI can connect to your APIs or execute custom python code)
- 🐋 Production Ready - 100% [dockerized](https://docs.docker.com/get-docker/)
- 👩‍👧‍👦 Active [Discord community](https://discord.gg/bHX5sNFCYU) and easy to understand [docs](https://cheshire-cat-ai.github.io/docs/)
 
We are committed to openness, privacy and creativity, we want to bring AI to the long tail. If you want to know more about our vision and values, read the [Code of Ethics](./readme/CODE-OF-ETHICS.md). 


## Roadmap

Detailed roadmap is [here](./readme/ROADMAP.md).
Whilst for the current progress of development, take a look at the [projects](https://github.com/orgs/cheshire-cat-ai/projects) marked as open.

## Contributing

To get the full dev setup, follow [install instructions](https://cheshire-cat-ai.github.io/docs/quickstart/installation-configuration/).
Send your pull request to the `develop` branch. Here is a [full guide to contributing](./readme/CONTRIBUTING.md).

Join our [community on Discord](https://discord.gg/bHX5sNFCYU) and give the project a star ⭐!
Thanks again!🙏

## Which way to go?

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<p align="center">
    <img align="center" src=./readme/cheshire-cat.jpeg width=400px alt="Wikipedia picture of the Cheshire Cat">
</p>

```
"Would you tell me, please, which way I ought to go from here?"
"That depends a good deal on where you want to get to," said the Cat.
"I don't much care where--" said Alice.
"Then it doesn't matter which way you go," said the Cat.

(Alice's Adventures in Wonderland - Lewis Carroll)

```
