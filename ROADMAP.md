
**Version 2.0 (temp)**

 - multimodality
 - graph (can be a plugin)
 - multiagent apis
 - review clients
 - all endpoints typed
 - function calling standard

**Version 1.8 (temp)**

 - custom endpoints (OK)
 - stress tests:
   - load testing (OK - https://github.com/lucagobbi/stressed-cat)
- form & tools
   - model getter (OK)
   - json schema + Pydantic support at choice
- telemetry
  - anonymous (just unique instance id, country, (n.utenti, info plugin))
- open issues (OK)
- community:
  - real pizza challenge (MAYBE)
  - meow talk (YT lives)

* **Version 1.5**
	* Technical 
		* Plugins
			* redesign hooks & tools signature (OK)
			* tools with more than one arg (Ok, working on forms)
			* no cat argument (OK, cat is a StrayCat)
			* registry online (OK)
		* Agent
			* Custom hookable agent
			* Async agent
			* Output dictionary retry (guardrails, kor, guidance)
			* Streaming (OK)
		* Unit tests 
			* Half coverage (OK)
		* Admin
			* sync / async calls consistent management (OK)
			* adapt to design system (OK)
			* show registry plugins (OK)
			* filters for memory search
		* Deploy
			* docker image! (OK)
			* compose with local LLM + embedder - ready to use (OK)
			* (nginx?)
		* LLM improvements
			* explicit support for chat vs completion (OK)
			* each LLM has its own default template (not relevant anymore)
		* User support (OK)
			* fix bugs (OK)
			* sessions (OK)
	* Outreach
		* Community
			* 1 live event (OK)
			* 4 meow talk (OK)
			* 1 challenge (KO)
		* Dissemination
			* use cases examples (OK)
			* tutorials on hooks (OK)
			* hook discovery tool (OK)
			* website analytics (OK)
		* Branding
			* logo (OK)
			* website + docs + admin design system (OK)

---

* **Version 1**
  * Forms from JSON schema ✅ 
  * Configurations
	  * Language model provider ✅ 
	  * Embedder ✅ 
  * Plugins list ✅ 
  * Why in the admin ✅ 
  * Documentation ✅ 
  * Markdown support ✅ 
  * Static admin inside main container ✅ 
  * [Public `/chat` endpoint](https://github.com/cheshire-cat-ai/core/issues/267/)  ✅
  * [js widget (for `/chat` and external websites)](https://github.com/cheshire-cat-ai/core/issues/269/) ✅
  * Memory management page in admin ✅
  * User management
    * User specific conversation and memory ✅
  * Dissemination
    * minimal website ✅
    * how to guides ✅
    * use cases examples
  * QA / Test
    * End2End tests
      * Setup ✅
      * Essential coverage ✅
    * Unit tests 
      * Setup ✅
      * Essential coverage ✅
  * Admin
    * import memories ✅
    * export memeories ✅
    * filters for memory search
    * better `why` UI ✅
  * Agent
    * Tool embeddings ✅
    * Custom hookable agent 
  * Local LLM / embedder ✅
    * CustomLLMConfig ✅
    * CustomEmbedderConfig adapters ✅
    * LLM / embedder example docker container ✅
  * Hook surface
    * 20 hooks ✅
    * more hooks where customization is needed ✅
  * Plugin management
    * Install plugin dependencies ✅
    * Activate / deactivate plugins ✅
    * External plugin directory ✅
    * Pugin manifesto (`plugin.json`) ✅
