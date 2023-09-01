from typing import Union, Callable, Literal, get_args

CAT_HOOKS = Literal[
    "rabbithole_instantiates_parsers",
    "before_rabbithole_stores_documents",
    "before_rabbithole_insert_memory",
    "before_rabbithole_splits_text",
    "rabbithole_splits_text",
    "after_rabbithole_splitted_text",
    "agent_prompt_instructions",
    "before_agent_starts",
    "agent_prompt_prefix",
    "agent_prompt_suffix",
    "agent_allowed_tools",
    "before_cat_bootstrap",
    "after_cat_bootstrap",
    "get_language_model",
    "get_language_embedder",
    "cat_recall_query",
    "before_cat_recalls_memories",
    "before_cat_recalls_episodic_memories",
    "before_cat_recalls_declarative_memories",
    "before_cat_recalls_procedural_memories",
    "after_cat_recalls_memories",
    "agent_prompt_episodic_memories",
    "agent_prompt_declarative_memories",
    "agent_prompt_chat_history",
    "before_cat_reads_message",
    "before_cat_sends_message",
    "before_collection_created",
    "after_collection_created",
]

# All @hook decorated functions in plugins become a CatHook.
class CatHook:

    def __init__(self, function: Callable, priority: int, hook_name: str = ""):
        
        self.function = function
        self.name = hook_name if hook_name else function.__name__
        self.priority = float(priority)

    def __repr__(self) -> str:
        return f"CatHook:\n - name: {self.name}, \n - priority: {self.priority}"

# @hook decorator. Any function in a plugin decorated by @hook and named properly (among list of available hooks) is used by the Cat
# @hook priority defaults to 1, the higher the more important. Hooks in the default core plugin have all priority=0 so they are automatically overwritten from plugins
def hook(*args: Union[str, Callable], priority: int = 1, name: CAT_HOOKS = "") -> Callable:
    def make_hook(func):
        return CatHook(
            func,
            priority=priority,
            hook_name=name
        )
    
    options = get_args(CAT_HOOKS)

    if name and name not in options:
        raise ValueError(f"The hook `{name}` is not valid. Valid hooks: {', '.join(options)}")
    
    if len(args) == 1 and callable(args[0]):
        # called as @hook
        return CatHook(
            function=args[0],
            priority=priority,
            hook_name=name
        )
    else:
        # called as @hook(*args, **kwargs)
        return make_hook
