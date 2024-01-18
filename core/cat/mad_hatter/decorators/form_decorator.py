from typing import List, Callable

from pydantic import BaseModel

from cat.mad_hatter.cat_form import CatForm, CatFormConfig

def form(intent_examples: List[str], strict: bool = False, return_direct = True) -> Callable:
    def wrapper(model_class: BaseModel):
        class NewForm(CatForm):

            config = CatFormConfig(
                intent_examples = intent_examples,
                strict = strict,
                return_direct = return_direct
            )

            model = model_class

        # Rename the NewForm subclass 
        new_name = f"{model_class.__name__}Form"
        new_form = type(new_name, (NewForm,), {'model': model_class})

        return new_form
    return wrapper

# Use of CatFormConfig to reduce the decorators arguments
# def form(form_config: CatFormConfig) -> Callable:
#     def wrapper(model_class: BaseModel):
#         class NewForm(CatForm):

#             config = form_config
#             model = model_class

#         # Rename the NewForm subclass 
#         new_name = f"{model_class.__name__}Form"
#         new_form = type(new_name, (NewForm,), {'model': model_class})

#         return new_form
#     return wrapper
