# Long Term Memory

The Cat's Long Term Memory (LTM) is made of two components:
- *episodic memory*, i.e. the context of documents uploaded to the Cat;
- *declarative memory*, i.e. the context of things the user said in the past.

These are nothing but two [vector databases](vector_memory.md) where memories are stored in the form of vectors.

By default, the Cat queries the LTM to retrieve the relevant context that is used to make up the [Main Prompt](../prompts/main_prompt.md).

### Long Term Memory flow :material-information-outline:{ title="click on the hooks node to see the hooks documentation" }

!!! note "Developer documentation"
    [Long Term Memory hooks](../../technical/plugins/hooks.md)

```mermaid
flowchart LR
    
```