import openai
from typing import List
from langchain import PromptTemplate

from cat.looking_glass.ws_logger import ws_logger

api_key = ""

# Shot is a class for prompt examples (few-shots learning)
class Shot:
    user: str
    assistant: str

    def __init__(self, user: str, assistant: str):
        self.user = "User: " + user
        self.assistant = "Assistant: " + assistant

    def __str__(self) -> str:
        return f"{self.user}\n{self.assistant}"


# LLM Transaction is a verbal or written exchange of single ideas or information between the agent and the user.
# Possible idea to speed up: Prompt pre-loading. Send in the main prompt before and then send only the query, this
# might speed things up. 
class LLMTransaction:

    shots: List[Shot] = []

    def __init__(self, template: str, model: str = "gpt-3.5-turbo") -> None:
        self.template = template
        self.model = model
        openai.api_key = api_key
    
    def set_shots(self, shots: List[Shot]) -> None:
        self.shots = shots
    
    def add_shot(self, shot: Shot) -> None:
        self.shots.append(shot)
    
    def format(self, query, **kwargs) -> str:
        prompt: str = self.template

        if(len(self.shots) > 0):
            prompt += f"\nExamples\n"
        
        for shot in self.shots:
            prompt += f"\n{str(shot)}"
        
        prompt: PromptTemplate = PromptTemplate.from_template(prompt)
        prompt: str = prompt.format(**kwargs)

        query: str = "QUERY: " + query
        
        prompt += f"\n\n{query}"

        return prompt

    def predict(self, query, **kwargs) -> str:
        prompt = self.format(query, **kwargs)
        messages = [{"role": "user", "content": prompt}]
        output = openai.ChatCompletion.create(model = self.model, messages = messages)
        return output.choices[0].message.content
    
class ChatHistory():
    history: List[dict] = []
    
    def get(self, i: int) -> dict:
        return self.history[i]

    def get_content(self, i: int) -> str:
        return self.get(i)["content"]

    def add_user_msg(self, msg: str) -> None:
        self.history.append({"role": "user", "content": msg})
    
    def add_assistant_msg(self, msg: str) -> None:
        self.history.append({"role": "assistant", "content": msg})
    
    def __str__(self) -> str:
        history_str = ""

        for i, his in enumerate(self.history):
            pref = "User: " if his["role"] == "user" else "Assistant: "
            history_str += (pref + his["content"] + ("" if i == len(self.history) - 1 else f"\n"))
        
        return history_str

    def remove_last(self) -> None:
        self.history = self.history[:-1]
    
    def remove(self, amount: int) -> None:
        self.history = self.history[:-amount]

    def purge(self) -> None:
        self.history = []

class LLMConversation:

    shots: List[Shot] = []
    messages: List[dict] = []

    def __init__(self, template: str, model: str = "gpt-3.5-turbo") -> None:
        self.template = template
        self.model = model
        openai.api_key = api_key
    
    def initialize(self, **kwargs) -> None:
        self.purge()

        first_message = self.format(**kwargs)
        self.messages = [{"role":  "user", "content": first_message}]

        print(self.messages[0]["content"])

    def set_shots(self, shots: List[Shot]) -> None:
        self.shots = shots

    def add_shot(self, shot: Shot) -> None:
        self.shots.append(shot)
    
    def format(self, **kwargs) -> str:
        prompt: str = self.template

        if(len(self.shots) > 0):
            prompt += f"\nExamples\n"
        
        for shot in self.shots:
            prompt += f"\n{str(shot)}"
        
        prompt: PromptTemplate = PromptTemplate.from_template(prompt)
        prompt: str = prompt.format(**kwargs)

        return prompt

    def predict(self, input: str):
        self.messages.append({"role": "user", "content": input})
        output = openai.ChatCompletion.create(model = self.model, messages = self.messages)
        self.messages.append(output.choices[0].message)
        return output.choices[0].message.content

    def purge(self) -> None:
        self.messages = []
    
    def remove_messages(self, num: int) -> None:
        self.messages = self.messages[:(-num)]
    
    def remove_messages_pair(self, num: int) -> None:
        self.messages = self.messages[:(-2 * num)]
    
    def remove_last_pair(self) -> None:
        self.remove_messages_pair(1)