import openai
import re

class Layer2LLM:
    def __init__(self, initial_prompt):
        openai.api_key = "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"
        self.initial_prompt = initial_prompt
        self.model = "gpt-3.5-turbo"
        # self.model = "gpt-3.5-turbo-16k"
        self.messages = [{"role": "system", "content": initial_prompt}]
        self.extract_tags()

    def predict(self, input) -> str:
        self.messages.append({"role": "user", "content": input})
        output = openai.ChatCompletion.create(model = self.model, messages = self.messages)
        self.messages.append(output.choices[0].message)
        return output.choices[0].message.content

    def extract_tags(self):
        regex = r"@([A-Z0-9]{10})"
        matches = re.findall(regex, self.initial_prompt)
        
        if(matches.__len__() != 2):
            raise ValueError("Wrong number of tags found in Layer2LLM.")
        
        # First tag in the prompt is the completion tag
        self.completion_tag = matches[0]

        # Second tag in the prompt is the exit tag
        self.exit_tag = matches[1]
    
    def is_completed(self) -> bool:
        if self.completion_tag in self.messages[self.messages.__len__() - 1]["content"]:
            return True
        return False
    
    def is_exit(self) -> bool:
        if self.exit_tag in self.messages[self.messages.__len__() - 1]["content"]:
            return True
        return False
    
    
    