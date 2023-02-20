from typing import Union, List

from langchain.agents import load_tools, initialize_agent
from langchain.agents import Tool, ZeroShotAgent, AgentExecutor
from pprint import pprint

class Tools:
    python_repl = "python_repl"
    serpapi = "serpapi"
    wolfram_alpha = "wolfram-alpha"
    requests = "requests"
    terminal = "terminal"
    pal_math = "pal-math"
    pal_colored_objects = "pal-colored-objects"
    llm_math = "llm-math"
    open_meteo_api = "open-meteo-api"
    news_api = "news-api"
    tmdb_api = "tmdb-api"
    google_search = "google-search"
    searx_search = "searx-search"
    google_serper = "google-serper"
    
    
    @classmethod
    def check_requirement(cls, tool:str) -> str: 
        requirements = {
            Tools.python_repl: """
Tool Name: Python REPL
Tool Description: A Python shell. Use this to execute python commands. Input should be a valid python command. If you expect output it should be printed out.
Notes: Maintains state.
Requires LLM: No            
            """,
            Tools.serpapi: """
Tool Name: Search
Tool Description: A search engine. Useful for when you need to answer questions about current events. Input should be a search query.
Notes: Calls the Serp API and then parses results.
Requires LLM: No            
            """,
            Tools.wolfram_alpha: """
Tool Name: Wolfram Alpha
Tool Description: A wolfram alpha search engine. Useful for when you need to answer questions about Math, Science, Technology, Culture, Society and Everyday Life. Input should be a search query.
Notes: Calls the Wolfram Alpha API and then parses results.
Requires LLM: No
Extra Parameters: wolfram_alpha_appid: The Wolfram Alpha app id.
            """,
            Tools.requests: """
Tool Name: Requests
Tool Description: A portal to the internet. Use this when you need to get specific content from a site. Input should be a specific url, and the output will be all the text on that page.
Notes: Uses the Python requests module.
Requires LLM: No            
            """,
            Tools.terminal: """
Tool Name: Terminal
Tool Description: Executes commands in a terminal. Input should be valid commands, and the output will be any output from running that command.
Notes: Executes commands with subprocess.
Requires LLM: No            
            """,
            Tools.pal_math: """
Tool Name: PAL-MATH
Tool Description: A language model that is excellent at solving complex word math problems. Input should be a fully worded hard word math problem.
Notes: Based on this paper (https://arxiv.org/pdf/2211.10435.pdf).
Requires LLM: Yes            
            """,
            Tools.pal_colored_objects: """
Tool Name: PAL-COLOR-OBJ
Tool Description: A language model that is wonderful at reasoning about position and the color attributes of objects. Input should be a fully worded hard reasoning problem. Make sure to include all information about the objects AND the final question you want to answer.
Notes: Based on this paper (https://arxiv.org/pdf/2211.10435.pdf).
Requires LLM: Yes
            """,
            Tools.llm_math: """
Tool Name: Calculator
Tool Description: Useful for when you need to answer questions about math.
Notes: An instance of the LLMMath chain.
Requires LLM: Yes            
            """,
            Tools.open_meteo_api: """
Tool Name: Open Meteo API
Tool Description: Useful for when you want to get weather information from the OpenMeteo API. The input should be a question in natural language that this API can answer.
Notes: A natural language connection to the Open Meteo API (https://api.open-meteo.com/), specifically the /v1/forecast endpoint.
Requires LLM: Yes            
            """,
            Tools.news_api: """
Tool Name: News API
Tool Description: Use this when you want to get information about the top headlines of current news stories. The input should be a question in natural language that this API can answer.
Notes: A natural language connection to the News API (https://newsapi.org), specifically the /v2/top-headlines endpoint.
Requires LLM: Yes
Extra Parameters: news_api_key (your API key to access this endpoint)
            """,
            Tools.tmdb_api: """
Tool Name: TMDB API
Tool Description: Useful for when you want to get information from The Movie Database. The input should be a question in natural language that this API can answer.
Notes: A natural language connection to the TMDB API (https://api.themoviedb.org/3), specifically the /search/movie endpoint.
Requires LLM: Yes
Extra Parameters: tmdb_bearer_token (your Bearer Token to access this endpoint - note that this is different from the API key)            
            """,
            Tools.google_search: """
Tool Name: Search
Tool Description: A wrapper around Google Search. Useful for when you need to answer questions about current events. Input should be a search query.
Notes: Uses the Google Custom Search API
Requires LLM: No
Extra Parameters: google_api_key, google_cse_id
For more information on this, see this page (https://langchain.readthedocs.io/en/latest/ecosystem/google_search.html)     
            """,
            Tools.searx_search: """
Tool Name: Search
Tool Description: A wrapper around SearxNG meta search engine. Input should be a search query.
Notes: SearxNG is easy to deploy self-hosted. It is a good privacy friendly alternative to Google Search. Uses the SearxNG API.
Requires LLM: No
Extra Parameters: searx_host            
            """,
            Tools.google_serper: """
Tool Name: Search
Tool Description: A low-cost Google Search API. Useful for when you need to answer questions about current events. Input should be a search query.
Notes: Calls the serper.dev Google Search API and then parses results.
Requires LLM: No
Extra Parameters: serper_api_key
For more information on this, see this page (https://langchain.readthedocs.io/en/latest/ecosystem/google_serper.html)       
            """,
        }
        return requirements.get(tool, None)


class AgentManager:
    """
    me servirebbe una mano a utilizzare agenti langchain a scelta e
    fare in modo che ne siano facilmente agganciati di custom
    """
    llm = None
    
    @classmethod
    def singleton(cls, llm):
        AgentManager.llm = llm
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

    
    @classmethod
    def get_agent(cls, tool_list:List(str), return_intermediate_steps=False):
        """get a list of tools and return an agent with the tools, the language model, and the type of agent we want to use

        Args:
            tool_list (List): example ["serpapi", "llm-math"] or [Tools.serpapi, Tools.llm_math]

        Returns:
            Agent: the agent initilized with tools and llm
            if return_intermediate_steps == False:
                agent.run("Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?")
                pprint(response["intermediate_steps"])
            else:
                response = agent({"input":"Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?"})
                print(response["intermediate_steps"])
                
                import json
                print(json.dumps(response["intermediate_steps"], indent=2))
        """
        good_tools = []
        for t in tool_list:
            if Tools.check_requirement(t) == None:
                pprint(f'NO specification for {t}')
            else:
                good_tools.append(t)
                
        tools = load_tools(good_tools, llm=AgentManager.llm)
        agent = initialize_agent(tools, AgentManager.llm, agent="zero-shot-react-description", verbose=True, return_intermediate_steps=True)
        return agent