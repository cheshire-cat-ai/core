from .cat_form import CatForm

# form decorator
def form(form: CatForm) -> CatForm:
    form._autopilot = True
    return form
