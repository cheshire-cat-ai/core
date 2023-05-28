# Plugins

Plugins are add-ons that can be installed to extend and customize the Cheshire Cat.  
A plugin is nothing but a collection of hook and tools.

## Hooks

The Cat uses functions knows as Hooks, which can be overridden, to customize the framework behavior in specific execution places.   
Hooks come with a *priority* property. 
The [plugins manager](cheshire_cat/mad_hatter.md) takes care of collecting all the hooks, sorting them in ascending order and executing them in descending order of priority.

## Tools

Tools are custom Python functions that are called by the [Agent](cheshire_cat/agent.md).   
These functions, provided by a rich docstring, end up in the [Main Prompt](prompts/main_prompt.md). 
In this way, the [Agent](cheshire_cat/agent.md) can make decisions about when and which tool is more suitable to fulfill the user's request.

!!! note "Developer documentation"   
    - [How to write a plugin](../technical/plugins/plugins.md)   
    - [Hooks](../technical/plugins/hooks.md)   
    - [Tools](../technical/plugins/tools.md)

