from fastapi.templating import Jinja2Templates

def get_jinja_templates():
    # Custom Jinja2 environment with changed delimiters
    # (to void conflicts with Vuejs/Alpine/whatever frontend frameworks)
    templates = Jinja2Templates(directory="cat/routes/static/core_static_folder/")
    templates.env.variable_start_string = '[['
    templates.env.variable_end_string = ']]'
    return templates