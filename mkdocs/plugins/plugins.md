# :electric_plug: How to write a plugin

To write a plugin just create a new folder in `core/cat/plugins/`. 

Add a python file to your plugin folder:

    ├── core
    │   ├── cat
    │   │   ├── plugins
    |   |   |   ├── myplugin
    |   |   |   |   ├ mypluginfile.py

Now let's start `mypluginfile.py` with a little import:

```python
from cat.mad_hatter.decorators import tool, hook
```

You are now ready to change the Cat's behavior using Tools and Hooks.


## :toolbox: Tools

Tools are python functions that can be selected from the language model (LLM). Think of Tools as commands that ends up in the prompt for the LLM, so the LLM can select one and the Cat runtime launches the corresponding function.  
Here is an example of Tool to let the Cat tell you what time it is:

```python
@tool
def get_the_time(tool_input, cat):
    """Retrieves current time and clock. Input is always None."""

    return str(datetime.now())
```

More examples on tools [here](tools.md)


## :hook: Hooks

Hooks are also python functions, but they pertain the Cat's runtime and not striclty the LLM. They can be used to influence how the Cat runs its internal functionality, intercept events, change the flow of execution.  

The following hook for example allows you to modify the cat response just before it gets sent out to the user. In this case we make a "grumpy rephrase" of the original response.

```python
@hook
def before_cat_sends_message(message, cat):

    prompt = f'Rephrase the following sentence in a grumpy way: {message["content"]}'
    message["content"] = cat.llm(prompt)

    return message
```

More examples on hooks [here](hooks.md)



