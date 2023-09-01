
* **Version 2**
	* Technical 
		* Plugins
			* redesign hooks & tools signature
			* tools with more than one arg (structured Tool)
			* no cat argument
			* registry online
		* Agent
			* Custom hookable agent
			* Async agent
			* Output dictionary retry (guardrails, kor, guidance)
			* (streaming?)
		* Unit tests 
			* Half coverage (main classes)
		* Admin
			* sync / async calls consistent management
			* adapt to design system
			* show registry plugins (core should send them alongside the installed ones)
			* filters for memory search
		* Deploy
			* docker image!
			* compose with local LLM + embedder - ready to use
			* (nginx?)
		* LLM improvements
			* explicit support for chat vs completion
			* each LLM has its own default template
		* User support (not management)
			* fix bugs
			* sessions
	* Outreach
		* Community
			* 1 live event
			* 4 meow talk
			* 1 challenge
		* Dissemination
			* use cases examples
			* tutorials on hooks
			* hook discovery tool
			* website analytics 
		* Branding
			* logo
			* website + docs + admin design system

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
