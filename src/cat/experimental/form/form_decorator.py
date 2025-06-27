from .cat_form import CatForm


# form decorator
def form(Form: CatForm) -> CatForm:
    Form._autopilot = True
    if Form.name is None:
        Form.name = Form.__name__

    if Form.triggers_map is None:
        Form.triggers_map = {
            "start_example": Form.start_examples,
            "description": [f"{Form.name}: {Form.description}"],
        }

    return Form
