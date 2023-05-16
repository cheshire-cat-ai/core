# :electric_plug: How to write a plugin

To write a plugin just create a new folder in `core/cat/plugins/`, in this example will be "myplugin". 

You need two python files to your plugin folder:

    ├── core
    │   ├── cat
    │   │   ├── plugins
    |   |   |   ├── myplugin
    |   |   |   |   ├ mypluginfile.py
    |   |   |   |   ├ plugin.json
    
The `plugin.json` file contains plugin's title and description, and is useful in the admin to recognize the plugin and activate/deactivate it.
If your plugin does not contain a `plugin.json` the cat will not block your plugin, but it is useful to have it.

`plugin.json` example:

```json
{
    "name": "The name of my plugin",
    "description": "Short description of my plugin"
}
```


Now let's start `mypluginfile.py` with a little import:

```python
from cat.mad_hatter.decorators import tool, hook
```

You are now ready to change the Cat's behavior using Hooks and Tools.


## :toolbox: Tools

Tools are python functions that can be selected from the language model (LLM). Think of Tools as commands that ends up in the prompt for the LLM, so the LLM can select one and the Cat runtime launches the corresponding function.  
Here is an example of Tool to let the Cat tell you what time it is:

```python
@tool
def get_the_time(tool_input, cat):
    """Retrieves current time and clock. Input is always None."""

    return str(datetime.now())
```

More examples on tools [here](tools.md).


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

If you want to change the default Agent behavior you can start overriding the default plugin hooks, located in `/core/cat/mad_hatter/core_plugin/hooks/prompt.py`, rewriting them in the plugin file with an higher priority. Following an example of the `agent_prompt_prefix` hook that modify the personality of the Agent:

```python

# Original Hook, from /core/cat/mad_hatter/core_plugin/hooks/prompt.py

@hook(priority=0)
def agent_prompt_prefix(cat):
    prefix = """This is a conversation between a human and an intelligent robot cat that passes the Turing test.
The cat is curious and talks like the Cheshire Cat from Alice's adventures in wonderland.
The cat replies are based on the Context provided below.

Context of things the Human said in the past:{episodic_memory}

Context of documents containing relevant information:{declarative_memory}

If Context is not enough, you have access to the following tools:
"""

    return prefix
```

```python

# Modified Hook, to be copied into mypluginfile.py

@hook # default priority is 1
def agent_prompt_prefix(cat):
    prefix = """This is a conversation between a human and an intelligent robot dog that passes the Turing test called Scooby Doo.
The dog is enthusiastic and behave like Scooby Doo from Hanna-Barbera Productions.
The dog replies are based on the Context provided below.

Context of things the Human said in the past:{episodic_memory}

Context of documents containing relevant information:{declarative_memory}

If Context is not enough, you have access to the following tools:
"""

    return prefix
```

Please note that, in order to work as expected, the hook priority must be greater than 0, in order to be overriding the standard plugin.
If you do not provide a priority, your hook will have `priority=1` and implicitly override the default one.

More examples on hooks [here](hooks.md).

