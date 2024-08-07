# Changelog

## 1.7.1 ( 2024-08-01 )

New in version 1.7

- User system
- permission system
- JWT support
- Custom Auth support
- White Rabbit
- StrayCat.classify

## 1.5.0 ( 2024-03-07 )

New in version 1.5.0: **Sir Punctilious Cat, the IV**! 

- `@form` and `CatForm` to build goal oriented conversation in plugins - @Pingdred, @MaxDam, @pieroit and pizza challenge contributors
- `@tool` `examples` to easily trigger tools - @zAlweNy26, @Pingdred
- Agent refactoring (both `forms` ant `tools` are unified under procedural memory) - @Pingdred, @pieroit
- Async tools - @Pingdred 
- Update Azure LLM - @cristianorevil 
- Update HuggingFaceEndpoints LLM - @alessioserra
- Dependencies update
- More unit tests, more stability

## 1.4.8 ( 2024-02-10 )

New in version 1.4.8

- fix Huggingface endpoint integration by @valentimarco 
- optimize plugins' dependencies checks by @kodaline and @pingdred
- adapter for OpenAI compatible endpoints by @AlessandroSpallina
- optimizations for temp files and logs by @pingdred
- Levenshtein distance utility by @horw
- customizable query param for recall functionality by @pazoff 
- alternative syntax for `@hook` by @zAlweNy26 
- `@tool` examples` by @zAlweNy26 
- ENV variable sfor Qdrant endpoint by @lucapirrone
- endpoints' final  `/` standardization by @zAlweNy26 
- logs refactoring by @giovannialbero1992
- chuck size and overlap in RabbitHole based on tokens by @nickprock 
- CustomOllama LLM adapter by @valentimarco 
- plugin upgradeability flag by @bositalia
- FatsEmbed base model and model enum by @nickprock and @valentimarco 
- bump langchain and openai versions by @Pingdred 
- new `before_cat_stores_episodic_memory` hook by @lucapirrone
- fix cat plugins folder bug in test suite by @nickprock 
- bump qdrant client version by @nickprock 

## (long time passed here without changelod updates)

## 0.0.5 ( 2023-06-05 )

### Enhancements

* `.env` file no more necessary for installation
* public chat to be customized under `/public`
* chat widget to be used on any website, from [this repo](https://github.com/cheshire-cat-ai/widget-vue)
* static file server under `/static`
* better logs with levels customizable in .env
* endpoint to reset conversation
* PR/issues templates
* .toml instead of requirements.txt
* faster and lighter image from Dockerfile
* `/admin` serves a static build of the admin from [this repo](https://github.com/cheshire-cat-ai/admin-vue)
* improved documentation, in a [new repo](https://github.com/cheshire-cat-ai/docs)
* new hooks

## 0.0.4 ( 2023-05-25 )

### Enhancements

* added more hooks (see `core_plugin`)
* added ethics code
* switched admin from React to Vue
* added `why` panel in the admin
* moved admin sources in a separate repo
* core serves a static build of the admin under `localhost:1865/admin`
* updated docs with plugin dev guide
* refactored the rabbithole
* plugins can have their own requirements.txt
* added support for Claude and PaLM


## 0.0.3 ( 2023-05-03 )

### Enhancements

* added more hooks to control prompting and allowed tools (see `core_plugin`)
* added `cat.working_memory` to store temporary and arbitrary info (recent convo, recalled memories, data shared by plugins)
* endpoints to erase memory contents (also completely wipe out memory)


## 0.0.2 ( 2023-04-28 )

### Enhancements

* introduction of `core_plugin` to have hooks and their defaults in beta before they are documented for plugin devs
* plugin system `MadHatter` sorts hooks by priority
* more hooks to control summarization prompt and reelaborate final reply to user
* chat autofocus and easier home navigation in admin
* support for Azure LLMs


## 0.0.1 ( 2023-04-20 )

### Enhancements

* Markdown support in admin
* Bump python version to 3.10 (remember to `docker-compose build --no-cache` after pull)
* Add host and port configuration via `.env`, please see `.env.example` as it is now necessary to declare default hosts and ports
* Update license to GPLv3
* Plugins list available in the admin
* endpoint `rabbithole/web` to ingest an URL, scrape it and store to memory
* Chat notification when finished uploading a file (sorta)
* Take back Qdrant as vector DB instead of FAISS, as FAISS does not allow metadata aware search
* Refactor CheshireCat class in smaller classes
