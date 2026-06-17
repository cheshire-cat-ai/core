<a name="readme-top"></a>

> [!WARNING]
> **Version 2 is super alpha!** This new version is still under heavy development and needs work before it becomes stable. Expect breaking changes, rough edges, and incomplete features. Not recommended for production use yet.

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h2>Cheshire Cat AI</h2>
  <h3>🇮🇹 Stregatto - 🇨🇳 柴郡貓 - 🇮🇳 चेशायर बिल्ली - 🇷🇺 Чеширский кот</h3>
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

## AI agent as a microservice

The Cheshire Cat is a framework to build custom AI agents:

- ⚡️ API first, to easily add a conversational layer to your app
- 🌐 Acts as an MCP client
- 🚀 Extensible via plugins
    - Extend endpoints
    - Custom multiple agents
    - Event callbacks
- 📱 Easy to use Web UI supporting the AGUI protocol
- 🦜 Supports any language model via adapter pattern
- 👥 Multiuser with granular permissions, SSO/Oauth2 compatible
- 🐋 100% dockerized
- 🦄 Active [Discord community](https://discord.gg/bHX5sNFCYU) and clear [docs](https://cheshire-cat-ai.github.io/docs/)
- (🐘 Built-in RAG with Qdrant) now a plugin


## Quickstart

To make Cheshire Cat run on your machine, you just need [`docker`](https://docs.docker.com/get-docker/) installed:

```bash
docker run --rm -it -p 1865:80 ghcr.io/cheshire-cat-ai/core:latest
```
- Chat with the Cheshire Cat on [localhost:1865](http://localhost:1865)
- Try out the REST API on [localhost:1865/docs](http://localhost:1865/docs)

Enjoy the Cat!  
Follow instructions on how to run it properly with [docker compose and volumes](https://cheshire-cat-ai.github.io/docs/quickstart/installation-configuration/).


## Docs and Resources

- [Official Documentation](https://cheshire-cat-ai.github.io/docs/)
- [Discord Server](https://discord.gg/bHX5sNFCYU)
- [Website](https://cheshirecat.ai/)
- [Tutorial - Write your first plugin](https://cheshirecat.ai/write-your-first-plugin/)


## Roadmap & Contributing

Detailed roadmap is [here](./ROADMAP.md).  
Send your pull request to the `develop` branch. Here is a [full guide to contributing](./CONTRIBUTING.md).

We are committed to openness, privacy and creativity, we want to bring AI to the long tail. If you want to know more about our vision and values, read the [Code of Ethics](./CODE-OF-ETHICS.md). 

Join our [community on Discord](https://discord.gg/bHX5sNFCYU) and give the project a star ⭐!
Thanks again!🙏

## License and trademark

Code is licensed under [GPL3](./LICENSE).  
The Cheshire Cat AI logo and name are property of Piero Savastano (founder and maintainer).

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
