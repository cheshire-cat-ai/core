
from cat.decorators import tool, prompt, hook

@tool
def mytool(inp):
    '''use this tool to fuck around'''
    return 'I AM THE CAAAAAAT'


@hook
def before_inserting_into_memory(stuff):
    return stuff


#@prompt
