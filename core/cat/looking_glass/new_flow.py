import openai
from typing import List
from langchain import PromptTemplate

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
        openai.api_key = "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"
    
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