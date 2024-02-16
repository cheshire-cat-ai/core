from typing import List, Dict
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, ValidationError

from cat.looking_glass.prompts import MAIN_PROMPT_PREFIX
from enum import Enum
from cat.log import log
import json


"""
@dataclass
class FieldExample:
    user_message: str
    model_before: Dict
    model_after:  Dict
    validation:   str
    responces:    List[str]
"""

# Conversational Form State
class CatFormState(Enum):
    INVALID         = 0
    VALID           = 1
    WAIT_CONFIRM    = 2


class CatForm:  # base model of forms
    description:     str
    model_class:     BaseModel
    start_examples:  List[str]
    stop_examples:   List[str]
    dialog_examples: List[Dict[str, str]]
 
    ask_confirm:   bool = False

    _autopilot = False
    

    def __init__(self, cat) -> None:
        self._state = CatFormState.INVALID
        self._model: Dict = {}
        
        self._cat = cat

        self._errors   = []
        self._ask_for  = []

        self._exit_threshold = 0.85
    

    @property
    def cat(self):
        return self._cat
    
    @property
    def ask_for(self) -> List:
        return self._ask_for
    
    @property
    def errors(self) -> List:
        return self._errors


    def close(self):
        """
        Clear Form on working memory
        """
        #TODO
        pass

    def submit(self, form_data) -> str:
        """
        Action
        """
        raise NotImplementedError


    # Check user confirm the form data
    def confirm(self) -> bool:
        
        # Get user message
        user_message = self.cat.working_memory["user_message_json"]["text"]
        
        # Confirm prompt
        confirm_prompt = \
f"""Your task is to produce a JSON representing whether a user is confirming or not.
JSON must be in this format:
```json
{{
    "confirm": // type boolean, must be `true` or `false`)    
}}
```

User said "{user_message}"

JSON:
```json
{{
    "confirm": """


        # Print confirm prompt
        print(confirm_prompt)

        # Queries the LLM and check if user is agree or not
        response = self.cat.llm(confirm_prompt)
        log.critical(f'check_user_confirm: {response}')
        
        return "true" in response.lower()
        
    

    # TOOD: now always False
    # Check if the user wants to exit the intent
    def check_exit_intent(self) -> bool:

        return False
        
        # TODO: To readjust the function code

        # Get user message vector
        user_message = self.cat.working_memory["user_message_json"]["text"]
        user_message_vector = self.cat.embedder.embed_query(user_message)
        
        # Search for the vector most similar to the user message in the vector database and get distance
        qclient = self.cat.memory.vectors.vector_db
        search_results = qclient.search(
            self.exit_intent_collection, 
            user_message_vector, 
            with_payload=False, 
            limit=1
        )
        print(f"search_results: {search_results}")
        nearest_score = search_results[0].score
        
        # If the nearest score is less than the threshold, exit intent
        return nearest_score >= self._exit_threshold

    # Execute the dialogue step
    def next(self):
        log.critical(self._state)

        # could we enrich prompt completion with episodic/declarative memories?
        #self.cat.working_memory["episodic_memories"] = []

        if self.check_exit_intent():
            self.close()
            return "`Form closed.`"

        # If state is WAIT_CONFIRM, check user confirm response..
        if self._state == CatFormState.WAIT_CONFIRM:
            if self.confirm():
                self.close()
                return self.submit(self._model)
            else:
                self._state = CatFormState.INVALID

        # If the state is INVALID, execute model update
        # (and change state based on validation result)
        if self._state == CatFormState.INVALID:
            self._model = self.update()

        # If state is VALID, ask confirm (or execute action directly)
        if self._state == CatFormState.VALID:
            if self.ask_confirm:
                self._state = CatFormState.WAIT_CONFIRM
            else:
                self.close() # TODO?
                return self.submit(self._model) # TODO?
            
        # if state is still INVALID, recap and ask for new info
        return self.message()


    # Updates the form with the information extracted from the user's response
    # (Return True if the model is updated)
    def update(self):

        # Conversation to JSON
        json_details = self.extract()
        json_details = self.sanitize(json_details)
        
        # model merge old and new
        new_model = self._model | json_details

        # Validate new_details
        new_model = self.validate(new_model)

        return new_model
    
    
    def message(self):

        if self._state == CatFormState.INVALID:
            out = f"""Info until now:

```json
{json.dumps(self._model, indent=4)}
```

I need //missing_fields//"""
        
            return out
        
        if self._state == CatFormState.WAIT_CONFIRM:
            return "Confirm? Yes or no?" 

    

    # Extract model informations from user message
    def extract(self):

        user_message = self.cat.working_memory["user_message_json"]["text"]
        chat_history = self.cat.working_memory["history"][-10:] # last n messages
        #log.warning(chat_history)

        # stringify history
        history = ""
        for turn in chat_history:
            history += f"\n - {turn['who']}: {turn['message']}"
        history += f"Human: {user_message}"

        # JSON structure
        # BaseModel.__fields__['my_field'].type_
        JSON_structure = "{"
        for field_name, field in self.model_class.model_fields.items():
            if field.description:
                description = field.description
            else:
                description = ""
            JSON_structure += f'\n\t"{field_name}": // {description} Must be of type `{field.annotation.__name__}`' # field.required?
        JSON_structure += "\n}"
    
        # TODO: reintroduce examples
        prompt = \
f"""Your task is to fill up a JSON out of a conversation.
The JSON must have this format:
```json
{JSON_structure}
```

This is the current JSON:
```json
{json.dumps(self._model, indent=4)}
```

This is the conversation:

{history}

Updated JSON:
```json
"""
        
#        if self._prompt_tpl_update:
#            prompt += self._prompt_tpl_update.format(
#                user_message = user_message, 
#                model = json.dumps(self._model)
#            )
#        else:
#            prompt += f"\
#                Sentence: {user_message}\n\
#                JSON:{json.dumps(self._model, indent=4)}\n\
#                Updated JSON:"
#            
        
        print(prompt)
        json_str = self.cat.llm(prompt, stream=True)
        # TODO: extract between '{' and '}' with regex
        json_str.replace("```", "") # TODO regex

        print(f"json after parser:\n{json_str}")
        try:
            output_model = json.loads(json_str)
        except:
            output_model = {} 
        return output_model


    # Sanitize model (take away unwanted keys and null values)
    # NOTE: unwanted keys are automatically taken away by pydantic
    def sanitize(self, model):

        # preserve only non-null fields
        model = {key: value for key, value in model.items() if value not in [None, '', 'None', 'null', 'lower-case']}

        return model


    # Validate model
    def validate(self, model):

        self._ask_for = []
        self._errors  = []
                
        try:
            # INFO TODO: In this case the optional fields are always ignored

            # Attempts to create the model object to update the default values and validate it
            model = self.model_class(**model).model_dump()

            # If model is valid change state to VALID
            self._state = CatFormState.VALID

        except ValidationError as e:
            
            # Collect ask_for and errors messages
            for error_message in e.errors():
                if error_message['type'] == 'missing':
                    self._ask_for.append(error_message['loc'][0])
                else:
                    self._errors.append(error_message["msg"])

            # Set state to INVALID
            self._state = CatFormState.INVALID

        return model


    # execute dialog prompt prefix
    def dialogue_prompt(self, prompt_prefix):
        log.critical(f"dialogue_prompt (state: {self._state})")

        # Get class fields descriptions
        class_descriptions = []
        for key, value in self.model_class.model_fields.items():
            class_descriptions.append(f"{key}: {value.description}")
        
        # Formatted texts
        formatted_model_class = ", ".join(class_descriptions)
        formatted_model       = ", ".join([f"{key}: {value}" for key, value in self._model.items()])
        formatted_ask_for     = ", ".join(self._ask_for) if self._ask_for else None
        formatted_errors      = ", ".join(self._errors) if self._errors else None
        
        formatted_validation  = ""
        if self._ask_for:
            formatted_validation  = f"information to ask: {formatted_ask_for}"
        if self._errors:
            formatted_validation  = f"there is an error: {formatted_errors}"

        prompt = prompt_prefix

        # If state is INVALID ask missing informations..
        if self._state in [CatFormState.INVALID]:
            # PROMPT ASK MISSING INFO
            prompt = \
                f"Your goal is to have the user fill out a form containing the following fields:\n\
                {formatted_model_class}\n\n\
                you have currently collected the following values:\n\
                {formatted_model}\n\n"

            if self._errors:
                prompt += \
                    f"and in the validation you got the following errors:\n\
                    {formatted_errors}\n\n"

            if self._ask_for:    
                prompt += \
                    f"and the following fields are still missing:\n\
                    {formatted_ask_for}\n\n"

            prompt += \
                f"ask the user to give you the necessary information."
            
            if self._prompt_tpl_response:
                prompt += "\n\n" + self._prompt_tpl_response.format(validation = formatted_validation)
                
        # If state is WAIT_CONFIRM (previous VALID), show summary and ask the user for confirmation..
        if self._state in [CatFormState.WAIT_CONFIRM]:
            # PROMPT SHOW SUMMARY
            prompt = f"Your goal is to have the user fill out a form containing the following fields:\n\
                {formatted_model_class}\n\n\
                you have collected all the available data:\n\
                {formatted_model}\n\n\
                show the user the data and ask them to confirm that it is correct.\n"

        # If state is UPDATE asks the user to change some information present in the model..
        if self._state in [CatFormState.UPDATE]:
            # PROMPT ASK CHANGE INFO
            prompt = f"Your goal is to have the user fill out a form containing the following fields:\n\
                {formatted_model_class}\n\n\
                you have collected all the available data:\n\
                {formatted_model}\n\n\
                show the user the data and ask him to provide the updated data.\n"


        # Print prompt prefix
        print(prompt)

        # Return prompt
        return prompt


"""
    # Load dialog examples by RAG
    def _load_dialog_examples_by_rag(self):    
        
        # TODO: The function code needs to be reviewed
        
        '''
        # Examples json format
        examples = [
            {
                "user_message": "I want to order a pizza",
                "model_before": "{{}}",
                "model_after":  "{{}}",
                "validation":   "information to ask: pizza type, address, phone",
                "response":     "What kind of pizza do you want?"
            },
            {
                "user_message": "I live in Via Roma 1",
                "model_before": "{{\"pizza_type\":\"Margherita\"}}",
                "model_after":  "{{\"pizza_type\":\"Margherita\",\"address\":\"Via Roma 1\"}}",
                "validation":   "information to ask: phone",
                "response":     "Could you give me your phone number?"
            },
            {
                "user_message": "My phone is: 123123123",
                "model_before": "{{\"pizza_type\":\"Diavola\"}}",
                "model_after":  "{{\"pizza_type\":\"Diavola\",\"phone\":\"123123123\"}}",
                "validation":   "information to ask: address",
                "response":     "Could you give me your delivery address?"
            },
            {
                "user_message": "I want a test pizza",
                "model_before": "{{\"phone\":\"123123123\"}}",
                "model_after":  "{{\"pizza_type\":\"test\", \"phone\":\"123123123\"}}",
                "validation":   "there is an error: pizza_type test is not present in the menu",
                "response":     "Pizza type is not a valid pizza"
            }
        ]
        '''

        # Get examples
        examples = self.dialog_examples()
        #print(f"examples: {examples}")

        # If no examples are available, return
        if not examples:
            return
        
        # Create example selector
        example_selector = SemanticSimilarityExampleSelector.from_examples(
            examples, self.cat.embedder, Qdrant, k=1, location=':memory:'
        )

        # Create example_update_model_prompt for formatting output
        example_update_model_prompt = PromptTemplate(
            input_variables = ["user_message", "model_before", "model_after"],
            template = "User Message: {user_message}\nModel: {model_before}\nUpdated Model: {model_after}"
        )
        #print(f"example_update_model_prompt:\n{example_update_model_prompt.format(**examples[1])}\n\n")

        # Create promptTemplate from examples_selector and example_update_model_prompt
        self._prompt_tpl_update = FewShotPromptTemplate(
            example_selector = example_selector,
            example_prompt   = example_update_model_prompt,
            suffix = "User Message: {user_message}\nModel: {model}\nUpdated Model: ",
            input_variables = ["user_message", "model"]
        )
        #print(f"prompt_tpl_update: {self._prompt_tpl_update.format(user_message='user question', model=self._model)}\n\n")

        # Create example_response_prompt for formatting output
        example_response_prompt = PromptTemplate(
            input_variables = ["validation", "response"],
            template = "Message: {validation}\nResponse: {response}"
        )
        #print(f"example_response_prompt:\n{example_response_prompt.format(**examples[1])}\n\n")

        # Create promptTemplate from examples_selector and example_response_prompt
        self._prompt_tpl_response = FewShotPromptTemplate(
            example_selector = example_selector,
            example_prompt   = example_response_prompt,
            suffix = "Message: {validation}\nResponse: ",
            input_variables = ["validation"]
        )
        #print(f"prompt_tpl_response: {self._prompt_tpl_response.format(validation='pydantic validation result')}\n\n")
""" 