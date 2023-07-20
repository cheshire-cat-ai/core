from cat.plugins.DbInteraction import Db
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain, create_extraction_chain_pydantic
from langchain.prompts import ChatPromptTemplate
from cat.mad_hatter.decorators import tool, hook

class prompt_utils():
    def __init__(self):
        pass
    def make_prompt_from_json(self, json):
        return "The menù of the restaurant is: \n" + self.dfs_dictionary(json)
    
    def get_initial_info(self):
        settings = Db.get_settings()
        suffix = "\n\nYou already have these informations"
        if "address" in settings:
            suffix += "\nHome address: " + settings["address"]
        if "card" in settings:
            suffix += "\nCard: " + settings["card"]
        return suffix



    def dfs_dictionary(self, input, depth: int):
        if(type(input) is dict):
            answer = ""
            for el in input.keys():
                answer += "\n"
                for int in range(depth):
                    answer = answer + "    "
                answer += el + ": " + self.dfs_dictionary(input[el], depth + 1)
        else:
            if(type(input) is list):
                answer = "\n"
                for int in range(depth):
                    answer += "    "
                for el in input:
                    answer += el + " - "
            else:
                answer = "\n"
                for int in range(depth):
                    answer += "    "
                answer += str(input)
        return answer
    
    def extract_informations(message: str, property: str, property_type: str, temperature: float, model: str, key: str):
        llm = ChatOpenAI(temperature=temperature, model=model, openai_api_key=key)

        schema = {
            "properties": {
                "restaurant_name": {"type": "string"},
            },
            "required": ["restaurant_name"],
        }

        chain = create_extraction_chain(schema, llm)

        out = chain.run(message)
        print(out)

        return out[0]["restaurant_name"]