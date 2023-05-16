# :hook: Hooks

Hooks are python functions that are called directly from the Cat at runtime.  
They allow you to change how the Cat does things by changing prompt, memory, endpoints and much more.

Both Hooks and Tools are python functions, but they have strong differences:

|                    | Hook                                                    | Tool                                                   |
|--------------------|:--------------------------------------------------------|:--------------------------------------------|
| Who invokes it     | The Cat                                                 | The LLM                                     |
| What it does       | Changes flow of execution and how data is passed around | Is just a way to let the LLM use functions  |
| Decorator          | `@hook`                                                 | `@tool`                                     |

## Available Hooks

Hooks will be listed and documented as soon as possible ( help needed! 😸 ).

At the moment you can hack around by exploring the available hooks in `core/cat/mad_hatter/core_plugin/hooks/`.
All the hooks you find in there define default Cat's behaviour and are ready to be overridden by your plugins.

## Examples

  1. How to change the prompt
  2. How to change how memories are saved and recalled
  3. How to access and use the working memory to share data around

## Hook search

TODO