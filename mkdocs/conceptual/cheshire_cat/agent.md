# Agent

The Agent is the Cat's component that handles the [tools](../plugins.md) execution.   
Sometimes a simple answer from the [language model](../llm.md#completion-model) is not enough. For this reason, the Cat can exploit a set of custom tools coming from the [plugins](../plugins.md). 
The decision on *whether* and *which* action should be taken to fulfill the user's request is delegated to the Agent component.

The Agent outlines a reasoning to take the aforementioned action.
By default, the structure of the Agent's reasoning is defined in the [instruction](../prompts/main_prompt.md#instructions) component of the [Main Prompt](../prompts/main_prompt.md).

The list of available tools can be manually filtered with hooks to condition the Agent's decision.

## Agent flow :material-information-outline:{ title="click on the nodes with hooks to see their documentation" }

!!! note "Developer documentation"
    [Agent hooks](../../technical/plugins/hooks.md)

Nodes with the :hook: point the execution places where there is an available [hook](../plugins.md) to customize the execution pipeline.
