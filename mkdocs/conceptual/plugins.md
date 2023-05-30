# Plugins

Plugins are add-ons that can be installed to extend and customize the Cheshire Cat.  
A plugin is nothing but a collection of hook and tools.

## Hooks

The Cat uses functions knows as Hooks, which can be overridden, to customize the framework behavior in specific execution places.   
Hooks come with a *priority* property. 
The [plugins manager](cheshire_cat/mad_hatter.md) takes care of collecting all the hooks, sorting and executing them in descending order of priority.

## Tools

Tools are custom Python functions that are called by the [Agent](cheshire_cat/agent.md).   
They come with a rich docstring upon with the [Agent](cheshire_cat/agent.md) choose *whether* and *which* tool is the most suitable to fulfill the user's request.
The list of available tools ends up in the [Main Prompt](prompts/main_prompt.md#instructions), where the [Agent](cheshire_cat/agent.md) receives instructions on how to structure its reasoning. 

!!! note "Developer documentation"   
    - [How to write a plugin](../technical/plugins/plugins.md)   
    - [Hooks](../technical/plugins/hooks.md)   
    - [Tools](../technical/plugins/tools.md)

