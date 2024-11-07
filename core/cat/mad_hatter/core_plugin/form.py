from pydantic import BaseModel
from cat.experimental.form import CatForm, form


class PizzaOrder(BaseModel):
    pizza_type: str
    phone: str
    address: str


@form
class PizzaForm(CatForm):
    description = "Pizza Order"
    model_class = PizzaOrder
    start_examples = [
        "order a pizza!",
        "I want pizza",
    ]
    stop_examples = [
        "stop pizza order",
        "not hungry anymore",
    ]
    ask_confirm = True

    def submit(self, form_data):
        return {
            "output": f"Pizza order on its way: {form_data}."
        }
