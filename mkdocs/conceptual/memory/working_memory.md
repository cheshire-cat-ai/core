# Working Memory

The Working Memory is a handful component to store temporary data.  
For instance, it can be used to share data across plugins or, in general, across any function that get an instance of the Cat as an argument.

By default, the Working Memory stores the *chat history* that ends up in the [Main Prompt](../prompts/main_prompt.md).
Moreover, the Working Memory collects the relevant context that is fetched from the *episodic* and *declarative* memories in the [Long Term Memory](long_term_memory.md).

## Working Memory flow :material-information-outline:{ title="click on the nodes with hooks to see their documentation" }

!!! note "Developer documentation"
    [Long Term Memory hooks](../../technical/plugins/hooks.md)

```mermaid
flowchart LR
    subgraph WM ["⚙️🐘️Working Memory"]
            direction TB
            CH[Chat History]
            C[Episodic Memory];
            D[Declarative Memory];
    end
    A["🐘Long Term Memory"] --> E["🪝"]; 
    E["🪝"] --> WM;
    CH --> main_prompt[Main Prompt];
    C --> main_prompt[Main Prompt];
    D --> main_prompt[Main Prompt];
```

Nodes with the :hook: point the execution places where there is an available [hook](../plugins.md) to customize the execution pipeline.
