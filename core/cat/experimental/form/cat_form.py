from typing import List, Dict
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError

from cat.looking_glass.prompts import MAIN_PROMPT_PREFIX
from enum import Enum
from cat.log import log
import json

from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain.vectorstores import Qdrant


@dataclass
class FieldExample:
    user_message: str
    model_before: Dict
    model_after:  Dict
    validation:   str
    responces:    List[str]


# Conversational Form State
class CatFormState(Enum):
    INVALID         = 0
    VALID           = 1
    WAIT_CONFIRM    = 2
    UPDATE          = 3


class CatForm:  # base model of forms

    model_class:     BaseModel
    start_examples:  List[str]
    stop_examples:   List[str]
    dialog_examples: List[Dict[str, str]]

    strict:        bool = False 
    ask_confirm:   bool = False
    return_direct: bool = True

    _autopilot = False


    def __init__(self, cat) -> None:
        self._state = CatFormState.INVALID
        self._model: Dict = Dict()
        
        self._cat = cat

        self._errors   = []
        self._ask_for  = []

        self._prompt_tpl_update   = None
        self._prompt_tpl_response = None
        self._load_dialog_examples_by_rag()

        self._exit_threshold = 0.85
    
    
    ##########################
    ####### PROPERTIES #######
    ##########################

    @property
    def cat(self):
        return self._cat
    
    @property
    def ask_for(self) -> []:
        return self._ask_for
    
    @property
    def errors(self) -> []:
        return self._errors


    ##############################
    ######## BASE METHODS ########
    ##############################
        
    def clear():
        """
        Clear Form on working memory
        """
        #TODO
        pass

    def submit(self, models) -> str:
        """
        Action
        """
        raise NotImplementedError
    

    ####################################
    ######## CHECK USER CONFIRM ########
    ####################################
        
    # Check user confirm the form data
    def confirm(self) -> bool:
        
        # Get user message
        user_message = self._cat.working_memory["user_message_json"]["text"]
        
        # Confirm prompt
        confirm_prompt = f"Given a sentence that I will now give you,\n\
        just respond with 'YES' or 'NO' depending on whether the sentence is:\n\
        - a refusal either has a negative meaning or is an intention to cancel the form (NO)\n\
        - an acceptance has a positive or neutral meaning (YES).\n\
        If you are unsure, answer 'NO'.\n\n\
        The sentence is as follows:\n\
        User message: {user_message}"
        
        # Print confirm prompt
        print("*"*10,
              f"\CONFIRM PROMPT:\n{confirm_prompt}\n",
              "*"*10)

        # Queries the LLM and check if user is agree or not
        response = self._cat.llm(confirm_prompt)
        log.critical(f'check_user_confirm: {response}')
        confirm = "NO" not in response and "YES" in response
        
        print("RESPONSE: " + str(confirm))
        return confirm
    

    ###################################
    ######## CHECK EXIT INTENT ########
    ###################################

    # Check if the user wants to exit the intent
    def check_exit_intent(self) -> bool:
        
        # TODO: To readjust the function code

        # Get user message vector
        user_message = self._cat.working_memory["user_message_json"]["text"]
        user_message_vector = self._cat.embedder.embed_query(user_message)
        
        # Search for the vector most similar to the user message in the vector database and get distance
        qclient = self._cat.memory.vectors.vector_db
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
    

    ####################################
    ############ UPDATE JSON ###########
    ####################################

    # Updates the form with the information extracted from the user's response
    # (Return True if the model is updated)
    def update(self):

        # User message to json details
        json_details = self.extract()
        if json_details is None:
            return False
        
        # model merge with details
        print("json_details", json_details)
        new_model = self._model_merge(json_details)
        print("new_model", new_model)
        
        # Check if there is no information in the new_model that can update the form
        if new_model == self._model:
            return False

        # Validate new_details
        new_model = self.validate(new_model)
                    
        # If there are errors, return false
        if len(self._errors) > 0:
            return False

        # Overrides the current model with the new_model
        self._model = new_model

        log.critical(f'MODEL : {self._model}')
        return True


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
            examples, self._cat.embedder, Qdrant, k=1, location=':memory:'
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
    

    # Model merge (actual model + details = new model)
    def _model_merge(self, json_details):
        # Clean json details
        json_details = {key: value for key, value in json_details.items() if value not in [None, '', 'None', 'null', 'lower-case']}

        # update form
        new_model = self._model | json_details
        
        # Clean json new_details
        new_model = {key: value for key, value in new_model.items() if value not in [None]}        
        return new_model


    # Extract model informations from user message
    def extract(self): 
        user_message = self._cat.working_memory["user_message_json"]["text"]
        
        prompt = "Update the following JSON with information extracted from the Sentence:\n\n"
        
        if self._prompt_tpl_update:
            prompt += self._prompt_tpl_update.format(
                user_message = user_message, 
                model = json.dumps(self._model)
            )
        else:
            prompt += f"\
                Sentence: {user_message}\n\
                JSON:{json.dumps(self._model, indent=4)}\n\
                Updated JSON:"
            
        json_str = self._cat.llm(prompt)
        print(f"json after parser: {json_str}")
        user_response_json = json.loads(json_str)
        return user_response_json


    # Validate model
    def validate(self, model):
        self._ask_for = []
        self._errors  = []

        # Reset state to INVALID
        self._state = CatFormState.INVALID
                
        try:
            # TODO: In this case the optional fields are always ignored

            # Pydantic model validate
            #self.model_class.model_validate(model)

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

        return model

    ####################################
    ######### EXECUTE DIALOGUE #########
    ####################################
    
    # Execute the dialogue step
    def dialogue(self):
        # Based on the strict setting it decides whether to use a direct dialogue or involve the memory chain 
        if self.strict is True:
            return self.dialogue_direct()
        else:
            return self.dialogue_action()


    # Execute the dialogue action
    def dialogue_action(self):
        log.critical(f"dialogue_action (state: {self._state})")

        #self._cat.working_memory["episodic_memories"] = []

        # If the state is INVALID or UPDATE, execute model update (and change state based on validation result)
        if self._state in [CatFormState.INVALID, CatFormState.UPDATE]:
            self.update()
            log.warning("> UPDATE")

        # If state is VALID, ask confirm (or execute action directly)
        if self._state in [CatFormState.VALID]:
            if self.ask_confirm is False:
                log.warning("> EXECUTE ACTION")
                self.close()
                return self.submit(self._model)
            else:
                self._state = CatFormState.WAIT_CONFIRM
                log.warning("> STATE=WAIT_CONFIRM")
                return None
            
        # If state is WAIT_CONFIRM, check user confirm response..
        if self._state in [CatFormState.WAIT_CONFIRM]:
            if self.confirm():
                log.warning("> EXECUTE ACTION")
                self.close()
                return self.submit(self._model)
            else:
                log.warning("> STATE=UPDATE")
                self._state = CatFormState.UPDATE
                return None

        return None
    

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
        print("*"*10, 
              f"\nPROMPT PREFIX:\n{prompt}\n", 
              "*"*10)

        # Return prompt
        return prompt


    # execute dialog direct (combines the previous two methods)
    def dialogue_direct(self):

        # check exit intent
        if self.check_exit_intent():
            log.critical(f'> Exit Intent {self.key}')
            self.close()
            return None
    
        # Get dialog action
        response = self.dialogue_action()
        if not response:
            # Build prompt
            user_message = self._cat.working_memory["user_message_json"]["text"]
            prompt_prefix = self._cat.mad_hatter.execute_hook("agent_prompt_prefix", MAIN_PROMPT_PREFIX, cat=self._cat)
            prompt_prefix = self.dialogue_prompt(prompt_prefix)
            prompt = f"{prompt_prefix}\n\n\
                User message: {user_message}\n\
                AI:"
            
            # Print prompt
            print("*"*10, 
                  f"\nPROMPT:\n{prompt}\n", 
                  "*"*10)

            # Call LLM
            response = self._cat.llm(prompt)

        return response
