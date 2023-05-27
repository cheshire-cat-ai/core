# :toolbox: Tools

A Tool is a python function that can be called directly from the language model.  
By "called" we mean that the LLM has a desciption of the available Tools in the prompt, and (given the conversation context) it can generate as output something like:

> Thought: Do I need to use a Tool? Yes  
> Action: search_ecommerce  
> Action Input: "white sport shoes"

So your `search_ecommerce` Tool will be called and given the input string `"white sport shoes"`.
The output of your Tool will go back to the LLM or directly to the user:

> Observation: "Mike air Jordania shoes are available for 59.99€"

You can use Tools to:

 - communicate with a web service
 - search information in an external database
 - execute math calculations
 - run stuff in the terminal (danger zone)
 - keep track of specific information and do fancy stuff with it
 - your fantasy is the limit!

Tools in the Cheshire Cat are inspired and extend [langchain Tools](https://python.langchain.com/en/latest/modules/agents/tools.html), an elegant [Toolformer](https://arxiv.org/abs/2302.04761) implementation.

## Your first Tool

A Tool is just a python function.
In your `mypluginfile.py` create a new function with the `@tool` decorator:

```python
@tool # (1)
def get_the_time(tool_input, cat): # (2)
    """Retrieves current time and clock. Input is always None.""" # (3)
    return str(datetime.now()) # (4)

```

1. Python functions in a plugin only become tools if you use the `@tool` decorator
2. Every `@tool` receives two arguments: a string representing the tool input, and the Cat instance. 
3. This doc string is necessary, as it will show up in the LLM prompt. It should describe what the tool is useful for and how to prepare inputs, so the LLM can select the tool and input it properly.
4. Always return a string, which goes back to the prompt informing the LLM on the Tool's output.

Let's see all the parts step by step...

TODO:

- a better example?
- show how tools are displayed in the prompt and how the LLM selects them
- more examples with little variations
    - the tool calls an external service
    - the tool reads/writes a file
    - the input string contains a dictionary (to be parsed with `json.loads`)
    - the tool manages a conversational form
    - `@tool(return_direct=True)` to let the returned string go straight to the chat
    - show how you can access cat's functionality (memory, llm, embedder, rabbit_hole) from inside a tool
    - what else? dunno
