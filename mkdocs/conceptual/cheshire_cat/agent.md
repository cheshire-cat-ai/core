# Agent

The Agent is the Cat's component that handles the [tools](../plugins.md) execution.   
Since sometimes an answer from the [language model](../llm.md) is not enough, the Cat can exploit a set of custom tools coming from the [plugins](../plugins.md). 
The decision on *when* and *which* action should be taken to fulfill the user's request is delegated to the Agent component.

By default, the structure of the Agent's reasoning is defined in the [instruction](../prompts/main_prompt.md#instructions) component of the [Main Prompt](../prompts/main_prompt.md).
Moreover, the list of available tool can be manually filtered.

## Agent flow :material-information-outline:{ title="click on the hooks node to see the hooks documentation" }

!!! note "Developer documentation"
    [Agent hooks](../../technical/plugins/hooks.md)

Nodes with the :hook: point the execution places where there is an available [hook](../plugins.md) to customize the execution pipeline.
