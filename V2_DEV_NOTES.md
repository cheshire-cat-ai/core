
# Version 2 dev notes

## Intro

- the good and the bad so far
- synthesis of many requests and common issues
- necessity to make maintaining easier
- new standards


## Installation

- user:
  ```bash
  uv init --bare mycat
  cd mycat
  uv python pin 3.13
  uv add cheshire-cat-ai
  uv run cat
  ```

- contributor:
  ```bash
  git clone ....
  cd core
  uv venv
  uv run cat
  ```

  To run linter and tests
  ```bash
  uv run ruff check
  uv run pytest tests
  ```

- github action:
  ```bash
  uv sync
  uv build
  uv publish --token={TOKEN}
  ```

- the docker is broken btw


## Agents

- Version 2 supports multiple agents, and the agent to be run can be chosen *per message*. So many agents can intervene in a single chat and they can communicate.
- you can declare an agent in your plugin subclassing the `Agent` and it will be automatically picked upo by core:

  ```python
  from cat import Agent
  
  TODO example
  ```
- If you want to achieve automatic routing between agents, you can define a custom routing agent (embedding based routing, LLM based routing, etc.). By default, core only requires you to specify an agent in chat request and that the agent is registered.
- So yes, now a plugin can contain one or more agents, and the agents can talk among themselves. I don't recommend such setups in production, but for sure having more agents and having the user decide which one to run, should allow more stable and useful AI apps.
- Agents can decide whether or not to run hooks, and even create new ones. Just call `await self.execute_hook("my_hook", default_value)` and everything works as it already worked.


## Plugins

- Most core functionality has been moved to plugins (still to be fixed and published). The vision is for a super slim core and more advanced plugins.
- There are many changes and most plugins need to be adjusted (will provide a dedicated guide). The old admin still works with v2 via core plugin `legacy_v1`.
- The cat vector memory can be completely deactivated, or some of it, and can be replaced/extended for example with a graph memory. See plugin `qdrant_vector_memory`
- Due to difficulties in keeping up with langchain, core only deals with internal types, based on MCP as a standard. All LLM and embedder vendors are now packed in a dedicated `llms` plugin so they are isolated and more easily maintained. This plugin uses vendor native libraries to convert between cat and vendor types. Langchain has been totally eradicated from the framework (you are still free to use it as a requirement in your plugin).
- plugins can contain tests inside a folder names `tests`. This folder will be ignored by the cat at runtime but tests will be run by `pytest`
- plugins settings are now saved and loaded from DB, so no more need for a local `settings.json`
- `load_settings` and `save_settings` are now async. Plugin overrides for those methods are not available anymore, since no one was using them.
- Settings pydantic model can have fields without a default value
- to access plugin data (settings, path) from within the plugin itself, you were doing:
  ```python
  # get current plugin path
  cat.mad_hatter.get_plugin().path
  # get plugin settings
  cat.mad_hatter.get_plugin().load_settings()
  ```
  Now you can do:
  ```python
  cat.plugin.path
  await cat.plugin.load_settings() # load_settings now is async
  ```
- plugin `settings_schema` is not overridable, only `settings_model` (as no one was using it)
- `vector_memory` creates separate collections for each used embedders, and if you switch back vectors are still there
  


## Network

- endpoints are placed under `/api/v2`. Plugins with custom endpoints can follow the convention or not. Root route `/` is not occupied by core and can be used from a plugin to serve a custom frontend - like the default `ui` plugin does.
- new `POST /message` endpoint that supports streaming (GIVE EXAMPLE), accepting `ChatRequest` and returning `ChatResponse` under both http and websocket. You can access this data structures in plugins with `cat.request` and `cat.response`. From within an agent, `self.request` and `self.response`. Note if you have a multi agent setup, all the agents will share this data structure. Any number of messages and custom data can be appended to `response.messages` and `response.custom`.
- When a client calls the cat, it can specify which agent to use in `ChatRequest.agent`. Default is `default`, which is similar to the old one, this time can run multiple tools in a row and builds prompt for each step. No more double prompt (there was one for tools and one for memory).
- conversation history endpoints (GET and POST) have been deleted and there is a new CRUD for chat sessions in plugin `ui`, which also includes the new multi-chat, multi-agent and multi-context frontend. Convo history as a recommended practice, must be passed via ws or http via `ChatRequest.messages` (similar to OpenAI or Ollama).
- when calling the Cat via websocket and http streaming, all tokens, notifications, agent steps, errors and other lifecycle events (including final response) will be sent following the [AG-UI](https://docs.ag-ui.com/concepts/events) protocol. 
- Settings, Plugins, Auth and Static endpoints have been refined and typed
  - details for each TODO
- plugin `ui` contains a ready to use CRUD for chats, which saves past chats to DB, allows searching and is completely detatched from core. Core only deals with actually running the conversation.

## Models

- from now on we only support chat models, text only or multimodal. Pure completion models are not supported anymore. If you need to use one, create your own LLM adapter and declare it subclassing `ModelProvider` .
- Embedders are not present in core, so are not automatically associated with the chosen LLM vendor. You will need to configure that yourself via an plugin or a custom one.


## Folder structure

- `plugins`, `static` and `data` folders live now in the root folder of a project, and are automatically created at first launch. In this way the cat can be used as a simple python package.
- A selection of plugins are automatically installed at first launch (in the future we can make this customizable)
- For the rest, the python package is absolutely stateless and stores no information whatsoever. Everything is either in the project folders or in the DB.


## Internals

- For v2, not being forced to respect retro-compatibility, I made a much requested move towards `async/await`. Important core contributors were pushing for this, and support for MCP made it a forced choice. The Cat now uses a single thread and should support way more concurrent requests. This implies that many methods that were simple functions, now are declared `async` and must be awaited with `await`.
- Some of the plugin primitives (hooks and tools) work both sync and async. More details on async below.
- (TODO: not really, better use AGUI custom event) - All websocket methods (`send_ws_message`, `send_chat_message`, `send_notification`, `send_error`) must be awaited as they are now async:

    ```python
        await send_ws_message(msg)
    ```
- also `cat.llm` is async and more rich in functionality so it can be used in endpoints and agents allowing flexibility:
  ```python
  async def llm(
      self,
      system_prompt: str,
      model: str | None = None,
      messages: list[Message] = [],
      tools: list[Tool] = [],
      stream: bool = True,
  ) -> Message:
  ```
- `StrayCat.working_memory.history` is not present anymore; in case we want to reimplment it `working_memory` should be a property getter/setter in `StrayCat` reading and writing a JSON to DB.
- Conversation history (and other context information) is passed by the client and easily found in `cat.request.messages`; history construction is delegated to clients and plugins (so you can decide whether to keep it stored client side, cat side - with custom endpoints - or another service side).
- A specialized factory is responsible to collect objects (auth handlers, LLMs, Agents) from plugins. The factory uses hooks to make this collection.
- `CatForm` used via the `@form` decorator is not included in core and have been moved to a plugin `form`. It was interesting to do research on this, but we ended up overengineering them: LLMs are way more powerful now and MCP has `elicitation` directly baked into tools. Furthermore, most of function calling fine tuning nowadays make the LLM itself ask for more info by inspecting the tool signature.
- Core DB is a simple SQL (supports both sqlite and postgres) and it is used to store settings, chats, contexts and plugin settings. No more `metadata.json`, no `qdrant` in core, no memory/file caches.
- Internal SQL is managed via Piccolo ORM (more about it later) and contains just two tables, `KeyValueDB` and `UserKeyValueDB`, acting as key/value stores respectively for global data and user specific data. There is also a couple of helpers to just call `.load` and `.save` XXXXXX examples. It's very easy to leverage core DB and Piccolo to add tables from plugins.
- Core defines also an abstract table called `UserScopedDB` that can be subclassed by plugins and used for custom CRUDs (chats, contexts, products, whatever).
- We've got a stabler and easier typing for Cat internals. Import the classes like this:
  ```python
  from cat.types import Message, Resource # and all other types
  ```
- Imports for most frequent used primitives are now simplified:
  ```python
  from cat import hook, tool, endpoint, log, Agent, ...
  from cat.auth import check_permissions, User, Auth
  ```
- factory explanation XXX
- Environment variables:
  - there are less env variables, as many things are delegated to plugins (which can decide whether to use them or not).
  - `CCAT_CORE_HOST`, `CCAT_CORE_PORT` and `CCAT_CORE_USE_SECURE_PROTOCOLS` have been collapsed into one single env variable `CCAT_URL` with default value `http://localhost:1865`
  - can get main paths and urls from `cat.paths` and `cat.urls`
  - `StrayCat` and `Agent` share `CatMixin` to use both llm, invoking agents, request/response and access to `CheshireCat` via `self.ccat`

## Hooks

- hooks `priority` fixed, the ones with a higher number go first.
- you have now in `cat.request` an object of type `ChatRequest`, containing user input and convo history, and in `cat.response` an object of type `ChatResponse`.  
`cat.response` is available since the beginning of the message flow. This is to avoid patterns in which devs stored in working memory stuff to be added later on in the final response via `before_cat_send_message`. Now you can store output data directly in `cat.response` and the client will receive that data.  
Both `cat.request` and `cat.response` are cleared at each message. Use `cat.working_memory` (if we decide to reimplement it) to store arbitrary information across the whole conversation.
- hooks can be declared sync, as in v1, and also async. The async version is recommended and the sync one will trigger a warning. Example:
  ```python
  @hook
  async def before_cat_sends_message(response, cat):
      mex = await cat.llm("...")
      response.append(mex)
      return response
  ```
- `before_agent_starts` hook now has no argument aside `cat`, as all context/agent_input is directly stored and inserted into prompt based on the content of working memory (you can hook this via `agent_prompt_suffix`)
- all hooks take two arguments, a value meant to be edited and the object calling the hook (being `CheshireCat`, `StrayCat` or `Agent`)


## Tools

- From now on we need to talk about internal and external (MCP) tools. Both are automatically converted to `Tool` and made available to the agents via `await self.list_tools()`.
- Tools can now accept multiple arguments, positional and keyword, thanks to the implemntation provided by Emanuele Morrone (@pingdred)
- Tool output can be a string, but now we allow also custom data structures and files via ToolOutput (Yet TODO). Tools will be able to return images, audio, files and resources of any kind - even UI pieces.


## Auth

Auth system semplifications (TODO review):

- (TODO) All endpoints, http and websocket, start closed (except XXXXX)
- You can now login into `/docs` using `CCAT_API_KEY`
- The default `CCAT_API_KEY` is `meow`.
- The default `CCAT_JWT_SECRET` is `meow_jwt`
- Both the key and the jwt must be sent via header `Authorization: Bearer xxx`.
- `CCAT_API_KEY_WS` does not exist anymore.
- If you are calling the cat machine-to-machine, use `CCAT_API_KEY`, for both http and ws. Websocket in a machine-to-machine settings supports headers, so you can follow the same schema (query parameter `?token=` is not supported anymore). TODO: still active just for dev v2
- If you are calling the cat form an unsecure client (a browser), use *only* jwt auth.
- You need to authenticate also to see `/docs` and there is a little form to do it in the page
- it is now possible to have `@endpoint` with custom resource and permissions. They can be defined on the endpoint and must be matched by user permissions (which can be assigned via Auth handler)
- A new installation by default only recognizes one user called `admin` with full permissions. Internal identity provider will ask directly for `CCAT_API_KEY` if you set one. This setup is perfect for development and personal usage, while for production either you use the Cat as a pure microservice, or implement SSO methods in your Auth handler.
- Auth handlers can be added by plugins by subclassing `Auth` and registering it via hook `factory_allowed_auth_handlers`.
- default Auth handler will not be active if other custom auth handlers are present
- if more than one custom auth handler is defined, they will be executed in sequence, and if one allows the request, access is granted. It's your responsibility to make sure only the desired auth handler(s) are active (they are also listed from endpoint `GET /status` for an easy check)
- Utilities to add and edit users have been eradicated from the framework, due to many complications, numerous niche requests from community, and the half baked solution that resulted in v1. Now Auth handlers can recognize users communicating with your identity provider of choice, core will ony deal with the `User` object as translated by the handler.


## MCP support

- this offers amazing opportunities for integration, as tens of thousands of MCP servers are now available. There are still just a few MCP clients, and the Cat is the furriest one.
- you can access the MCP client directly from the `StrayCat`:
  ```python
      tools = await cat.list_tools()
      prompts = await cat.list_prompts()
      resources = await cat.list_resources()
  ```
  or from within an agent:
  ```python
      tools = await self.list_tools()
      prompts = await self.list_prompts()
      resources = await self.list_resources()
  ```

  Note `list_tools` gives a list of `Tool` objects, which uniform both intenral plugin tools and MCP tools.
- you can connect to the cat only MCP servers that have http transport. Do not even try to ask me to run stdio based servers inside the cat. Use a proper proxy and aggregator for your local stuff, for example [MetaMCP](https://docs.metamcp.com/en).


## Others

- all http errors, both the ones coming from the cat and the ones coming from fastAPI validation, return an `HTTPException`
- static files are protected and organized in folders, one per user, with an hashed name.


## TODO

### agents

- Provide easy methods to load and save resources / memories (after refactoring the vector memory plugin)
- Remove `Context` object: flatten state onto Agent (`self.task`, `self.result`, `self.system_prompt`, `self.tools`, etc.). Directives receive the agent instance directly.
- Directives lifecycle: add `.start(agent)`, `.step(agent)`, `.finish(agent)` to map before-loop / each-iteration / after-loop phases. Loop resets `system_prompt` before each `.step()` so directives don't accumulate.
- Hooks should modify stuff in place (agent, tools list, prompt, etc.), no need to force a return value like it is now

### auth

- SSO infrastructure implementation
- refine `Auth`
- when default auth is not active, `/auth/internal-idp` endpoint should return 403

### core plugins

- recover still missing core plugins
- update core plugins so they attach to hooks exposed by core and provide their own hooks for other plugins
- how do plugins check for support or the presence of other plugins? (maybe `cat.get_plugin("vector_memory") -> Plugin | None`)

### tests

- core tests deeply broken
- core tests should only deal with core (also because plugin install dependencies is mocked!!!)
- tests for plugins should be automatically executed

### settings

- multipage plugin settings
- user based settings `cat.user.load_settings()`
- `cat.plugin.load_settings` should allow to choose the format (`as_dict=True` otherwise return directly the pydantic obj)
- `cat.plugin.save_settings` should accept both a dictionary or a pydantic model
- `settings.py` file in project path alà django, and if not in any case get rid of `get_env`

### other

- AG-UI should send `event: {xxx}`, leave `data: {xxx}` for the legacy messaging style 
- some packages used by core occupy a lot of space and do basically nothing (find alts)
  `du -h .venv/lib/python3.13/site-packages --max-depth=1 | sort -hr`
- `@hook` decorator should support autocomplete for the hooks names, and allow custom strings
- check for memory leaks (see Luca Gobbi's setup for locust)
- `cat` argument in hooks and tools should be optional
- wrap internal tables (key value store) in easy to use get/set methods (the user related one accessible directly from `User` object)
- static folder segregated by user already in `/data/uploads`, but endpoints broken


## Questions

- as there are docker and pyPI releases, does it make sense to have a `develop` branch?
- move plugin settings out of plugin folder and into DB?
- should we keep the working_memory functionality? In case, `working_memory` can be a property/setter of StrayCat internally loading/saving a JSON from `UserKeyValueDB` table
- should plugin methods `load_settings` and `save_settings` work both with dictionaries and pydantic objects?
- when should the factory run? at cat startup or at each StrayCat request? (the second may slow down but allows for user specific injection of objects)
- class `User` has UUID as id, not sure would be more flexible to have a str

## Challenges

- Create an "auto" agent that automatically redirects execution to the most competent agent (TODO agents should have a description)
- Log into the Cat with your Google account
