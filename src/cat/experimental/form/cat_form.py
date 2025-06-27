import json
from enum import Enum
from typing import List, Dict
from pydantic import BaseModel, ValidationError

from cat.utils import parse_json
from cat.log import log


# Conversational Form State
class CatFormState(Enum):
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"
    WAIT_CONFIRM = "wait_confirm"
    CLOSED = "closed"


class CatForm:  # base model of forms
    model_class: BaseModel
    procedure_type: str = "form"
    name: str = None
    description: str
    start_examples: List[str]
    stop_examples: List[str] = []
    ask_confirm: bool = False
    triggers_map = None
    _autopilot = False

    def __init__(self, cat) -> None:
        self._state = CatFormState.INCOMPLETE
        self._model: Dict = {}

        self._cat = cat

        self._errors: List[str] = []
        self._missing_fields: List[str] = []

    @property
    def cat(self):
        return self._cat

    def model_getter(self):
        return self.model_class

    def submit(self, form_data) -> str:
        raise NotImplementedError

    # Check user confirm the form data
    def confirm(self) -> bool:
        # Get user message
        user_message = self.cat.working_memory.user_message_json.text

        # Confirm prompt
        confirm_prompt = f"""Your task is to produce a JSON representing whether a user is confirming or not.
JSON must be in this format:
```json
{{
    "confirm": // type boolean, must be `true` or `false` 
}}
```

User said "{user_message}"

JSON:
{{
    "confirm": """

        # Queries the LLM and check if user is agree or not
        response = self.cat.llm(confirm_prompt)
        return "true" in response.lower()

    # Check if the user wants to exit the form
    # it is run at the befginning of every form.next()
    def check_exit_intent(self) -> bool:
        # Get user message
        user_message = self.cat.working_memory.user_message_json.text

        # Stop examples
        stop_examples = """
Examples where {"exit": true}:
- exit form
- stop it"""

        for se in self.stop_examples:
            stop_examples += f"\n- {se}"

        # Check exit prompt
        check_exit_prompt = f"""Your task is to produce a JSON representing whether a user wants to exit or not.
JSON must be in this format:
```json
{{
    "exit": // type boolean, must be `true` or `false`
}}
```

{stop_examples}

User said "{user_message}"

JSON:
"""

        # Queries the LLM and check if user is agree or not
        response = self.cat.llm(check_exit_prompt)
        return "true" in response.lower()

    # Execute the dialogue step
    def next(self):
        # could we enrich prompt completion with episodic/declarative memories?
        # self.cat.working_memory.episodic_memories = []

        # If state is WAIT_CONFIRM, check user confirm response..
        if self._state == CatFormState.WAIT_CONFIRM:
            if self.confirm():
                self._state = CatFormState.CLOSED
                return self.submit(self._model)
            else:
                if self.check_exit_intent():
                    self._state = CatFormState.CLOSED
                else:
                    self._state = CatFormState.INCOMPLETE

        if self.check_exit_intent():
            self._state = CatFormState.CLOSED

        # If the state is INCOMPLETE, execute model update
        # (and change state based on validation result)
        if self._state == CatFormState.INCOMPLETE:
            self.update()

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
        self._model = self._model | json_details

        # Validate new_details
        self.validate()


    def message(self):
        state_methods = {
            CatFormState.CLOSED: self.message_closed,
            CatFormState.WAIT_CONFIRM: self.message_wait_confirm,
            CatFormState.INCOMPLETE: self.message_incomplete,
        }
        state_method = state_methods.get(
            self._state, lambda: {"output": "Invalid state"}
        )
        return state_method()

    def message_closed(self):
        return {"output": f"Form {type(self).__name__} closed"}

    def message_wait_confirm(self):
        output = self._generate_base_message()
        output += "\n --> Confirm? Yes or no?"
        return {"output": output}

    def message_incomplete(self):
        return {"output": self._generate_base_message()}

    def _generate_base_message(self):
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
        return out

    # Extract model informations from user message
    def extract(self):
        prompt = self.extraction_prompt()

        json_str = self.cat.llm(prompt)

        # json parser
        try:
            output_model = parse_json(json_str)
        except Exception as e:
            output_model = {}
            log.warning("LLM did not produce a valid JSON")
            log.warning(e)

        return output_model

    def extraction_prompt(self):
        history = self.cat.working_memory.stringify_chat_history()

        # JSON structure
        # BaseModel.__fields__['my_field'].type_
        JSON_structure = "{"
        for field_name, field in self.model_getter().model_fields.items():
            if field.description:
                description = field.description
            else:
                description = ""
            JSON_structure += f'\n\t"{field_name}": // {description} Must be of type `{field.annotation.__name__}` or `null`'  # field.required?
        JSON_structure += "\n}"

        # TODO: reintroduce examples
        prompt = f"""Your task is to fill up a JSON out of a conversation.
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
"""

        # TODO: convo example (optional but supported)

        prompt_escaped = prompt.replace("{", "{{").replace("}", "}}")
        return prompt_escaped

    # Sanitize model (take away unwanted keys and null values)
    # NOTE: unwanted keys are automatically taken away by pydantic
    def sanitize(self, model):
        # preserve only non-null fields
        null_fields = [None, "", "None", "null", "lower-case", "unknown", "missing"]
        model = {key: value for key, value in model.items() if value not in null_fields}

        return model

    # Validate model
    def validate(self):
        self._missing_fields = []
        self._errors = []

        try:
            # INFO TODO: In this case the optional fields are always ignored

            # Attempts to create the model object to update the default values and validate it
            self.model_getter()(**self._model).model_dump(mode="json")

            # If model is valid change state to COMPLETE
            self._state = CatFormState.COMPLETE

        except ValidationError as e:
            # Collect ask_for and errors messages
            for error_message in e.errors():
                field_name = error_message["loc"][0]
                if error_message["type"] == "missing":
                    self._missing_fields.append(field_name)
                else:
                    self._errors.append(f'{field_name}: {error_message["msg"]}')
                    del self._model[field_name]

            # Set state to INCOMPLETE
            self._state = CatFormState.INCOMPLETE