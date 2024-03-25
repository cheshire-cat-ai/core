from langchain.chains import LLMChain
from langchain_core.prompts.prompt import PromptTemplate
import re

# Receives as input an action enum (ActionName and Description) and a user message, 
# and based on that chooses which element of the enum to return (the first element is by default)
def classify(cat, actions, user_message):

    # Get default action (first element)
    default_action = next(iter(actions))

    # Compose prompt
    prompt = f"""
Your task is to produce a JSON representing which action the user chooses based on UserMessage. 
The possible actions are the following, in case of doubt answer with <{default_action.name}>:
"""
    for action in actions:
        prompt += f"\n<{action.name}> {action.value}"
        
    prompt += f"""
    
and return the corresponding tag for the action to be taken in the JSON format,
JSON must be in this format:
{{
    "action": "<{default_action.name}>"
}}
User said "{user_message}"

JSON:
```json
{{
    "action":"""

    # Escape curly braces in the prompt
    prompt = prompt.replace("{", "{{").replace("}", "}}")

    # Invoke LLM chain
    response = call_llm_and_extract_json(cat, prompt)
    
    # Locates the returned action
    for action in actions:
        if "<" + action.name + ">" in response.upper():
            return action
    return default_action

# Call LLM and extract json from the response
def call_llm_and_extract_json(cat, prompt):
    
    # For Debug
    #response = cat.llm(prompt, stream=True)
	#print(f"response without chain:\n{response}")

    # Escape curly braces in the prompt
    prompt = prompt.replace("{", "{{").replace("}", "}}")

    # Invoke LLM chain
    extraction_chain = LLMChain(
        prompt     = PromptTemplate.from_template(prompt),
        llm        = cat._llm,
        verbose    = True,
        output_key = "output"
    )
    
    # Stops the acquisition if it finds the end of the json
    response = extraction_chain.invoke({"stop": ["}"]})["output"] + "}"
    
    # For Debug
    #print(f"Reponse before parser:\n{response}")

    # Extracts the json from the response
    match_json = re.search(r'\{[^{}]*\}', response)
    response = match_json.group() if match_json else response

    # Removes any comments in the json
    match_comments = r'//.*?\n'
    response = re.sub(match_comments, '', response)

    # For Debug
    #print(f"Reponse after parser:\n{response}")

    return response