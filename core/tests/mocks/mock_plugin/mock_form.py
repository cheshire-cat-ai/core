from typing import List, Dict
from datetime import date, time
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from cat.log import log
from cat.experimental.form import form, CatForm

class PizzaBorderEnum(Enum):
    HIGH = "high"
    LOW = "low"

# simple pydantic model
class PizzaOrder(BaseModel):
    pizza_type: str
    pizza_border: PizzaBorderEnum
    phone: str = Field(max_length=10)

@form
class PizzaForm(CatForm):
    description = "Pizza Order"
    model_class = PizzaOrder
    start_examples = [
        "order a pizza",
        "I want pizza"
    ]
    stop_examples = [
        "stop pizza order",
        "I do not want a pizza anymore",
    ]

    ask_confirm: bool = True

    def submit(self, form_data):
        
        msg = f"Form submitted: {form_data}"
        #self.cat.send_ws_message(msg, msg_type="chat")
        return {
            "output": msg
        }