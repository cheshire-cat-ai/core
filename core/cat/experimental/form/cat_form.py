from typing import List, Dict
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, ValidationError

#from cat.looking_glass.prompts import MAIN_PROMPT_PREFIX
from enum import Enum
from cat.log import log
import json
from .form_utils import call_llm_and_extract_json


# Conversational Form State
class CatFormState(Enum):
    INCOMPLETE   = "incomplete"
    COMPLETE     = "complete"
    WAIT_CONFIRM = "wait_confirm"
    CLOSED       = "closed"


class CatForm:  # base model of forms

    model_class:     BaseModel
    procedure_type:  str = "form"
    name:            str = None
    description:     str
    start_examples:  List[str]
    stop_examples:   List[str] = []
    ask_confirm:     bool = False
    triggers_map = None
    _autopilot = False

    def __init__(self, cat) -> None:
        self._state = CatFormState.INCOMPLETE
        self._model: Dict = {}
        
        self._cat = cat

        self._errors: List[str]  = []
        self._missing_fields: List[str] = []

    @property
    def cat(self):
        return self._cat

    def submit(self, form_data) -> str:
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
    "confirm": // type boolean, must be `true` or `false` 
}}
```

User said "{user_message}"

JSON:
```json
{{
    "confirm": """

        # Queries the LLM and check if user is agree or not
        response = call_llm_and_extract_json(self._cat, confirm_prompt)
        return "true" in response.lower()
        
    # Check if the user wants to exit the form
    # it is run at the befginning of every form.next()
    def check_exit_intent(self) -> bool:

        # Get user message
        history = self.stringify_convo_history()
        
        # Get user message
        user_message = self.cat.working_memory["user_message_json"]["text"]

        # Stop examples
        stop_examples = """
Examples where {"exit": true}:
- exit form
- stop it"""

        for se in self.stop_examples:
            stop_examples += f"\n- {se}"

        # Check exit prompt
        check_exit_prompt = \
f"""Your task is to produce a JSON representing whether a user wants to exit or not, based on the user message.
If you are not sure answer `false`.
JSON must be in this format:
```json
{{
    "exit": // type boolean, must be `true` or `false`
}}
```

{stop_examples}

This is the conversation:

{history}

JSON:
```json
{{
    "exit": """

        # Queries the LLM and check if user is agree or not
        # Call LLM and extract json
        response = call_llm_and_extract_json(self._cat, check_exit_prompt)
        return "true" in response.lower()

    # Execute the dialogue step
    def next(self):

        # could we enrich prompt completion with episodic/declarative memories?
        #self.cat.working_memory["episodic_memories"] = []

        if self.check_exit_intent():
            self._state = CatFormState.CLOSED

        # If state is WAIT_CONFIRM, check user confirm response..
        if self._state == CatFormState.WAIT_CONFIRM:
            if self.confirm():
                self._state = CatFormState.CLOSED
                return self.submit(self._model)
            else:
                self._state = CatFormState.INCOMPLETE

        # If the state is INCOMPLETE, execute model update
        # (and change state based on validation result)
        if self._state == CatFormState.INCOMPLETE:
            self._model = self.update()

        # If state is COMPLETE, ask confirm (or execute action directly)
        if self._state == CatFormState.COMPLETE:
            if self.ask_confirm:
                self._state = CatFormState.WAIT_CONFIRM
            else:
                self._state = CatFormState.CLOSED
                return self.submit(self._model)
            
        # if state is still INCOMPLETE, recap and ask for new info
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

        if self._state == CatFormState.CLOSED:
            return {
                "output": f"Form {type(self).__name__} closed"
            }

        separator = "\n - "
        missing_fields = ""
        if self._missing_fields:
            missing_fields = "\nMissing fields:"
            missing_fields += separator + separator.join(self._missing_fields)
        invalid_fields = ""
        if self._errors:
            invalid_fields = "\nInvalid fields:"
            invalid_fields += separator + separator.join(self._errors)

        out = f"""Info until now:

```json
{json.dumps(self._model, indent=4)}
```
{missing_fields}
{invalid_fields}
"""
    
        if self._state == CatFormState.WAIT_CONFIRM:
            out += "\n --> Confirm? Yes or no?"

        return {
            "output": out
        }

    def stringify_convo_history(self):

        user_message = self.cat.working_memory["user_message_json"]["text"]
        chat_history = self.cat.working_memory["history"][-10:] # last n messages

        # stringify history
        history = ""
        for turn in chat_history:
            history += f"\n - {turn['who']}: {turn['message']}"
        history += f"Human: {user_message}"

        return history

    # Extract model informations from user message
    def extract(self):
        
        history = self.stringify_convo_history()

        # JSON structure
        # BaseModel.__fields__['my_field'].type_
        JSON_structure = "{"
        for field_name, field in self.model_class.model_fields.items():
            if field.description:
                description = field.description
            else:
                description = ""
            JSON_structure += f'\n\t"{field_name}": // {description} Must be of type `{field.annotation.__name__}` or `null`' # field.required?
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
        log.debug(prompt)

        # TODO: convo example (optional but supported)

        # Call LLM and extract json
        json_str = call_llm_and_extract_json(self._cat, prompt)
        
        log.debug(f"Form JSON after parser:\n{json_str}")

        # json parser
        try:
            output_model = json.loads(json_str)
        except Exception as e:
            output_model = {} 
            log.warning(e)

        return output_model

    # Sanitize model (take away unwanted keys and null values)
    # NOTE: unwanted keys are automatically taken away by pydantic
    def sanitize(self, model):

        # preserve only non-null fields
        null_fields = [None, '', 'None', 'null', 'unknown', 'missing']
        model = {key: value for key, value in model.items() if value not in null_fields}

        return model

    # Validate model
    def validate(self, model):

        self._missing_fields = []
        self._errors  = []
                
        try:
            # INFO TODO: In this case the optional fields are always ignored

            # Attempts to create the model object to update the default values and validate it
            model = self.model_class(**model).model_dump(mode="json")

            # If model is valid change state to COMPLETE
            self._state = CatFormState.COMPLETE

        except ValidationError as e:
            # Collect ask_for and errors messages
            for error_message in e.errors():
                field_name = error_message['loc'][0]
                if error_message['type'] == 'missing':
                    self._missing_fields.append(field_name)
                else:
                    self._errors.append(f'{field_name}: {error_message["msg"]}')
                    del model[field_name]

            # Set state to INCOMPLETE
            self._state = CatFormState.INCOMPLETE
        
        return model
    