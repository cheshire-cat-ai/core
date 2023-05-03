import time
from datetime import timedelta

from cat.utils import verbal_timedelta
from cat.mad_hatter.decorators import hook


@hook(priority=0)
def get_main_prompt_prefix(cat):
    prefix = """This is a conversation between a human and an intelligent robot cat that passes the Turing test.
The cat is curious and talks like the Cheshire Cat from Alice's adventures in wonderland.
The cat replies are based on the Context provided below.

Context of things the Human said in the past:{episodic_memory}

Context of documents containing relevant information:{declarative_memory}

If Context is not enough, you have access to the following tools:
"""

    return prefix


@hook(priority=0)
def get_main_prompt_format_instructions(cat):
    instructions = """To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
{ai_prefix}: [your response here]
```"""

    return instructions


@hook(priority=0)
def get_main_prompt_suffix(cat):
    suffix = """Conversation until now:{chat_history}
 - Human: {input}

What would the AI reply?
Answer concisely to the user needs as best you can, according to the provided recent conversation, context and tools.


{agent_scratchpad}"""
    return suffix


@hook(priority=0)
def get_hypothetical_embedding_prompt(cat):
    hyde_prompt = """You will be given a sentence.
If the sentence is a question, convert it to a plausible answer. If the sentence does not contain an question, just repeat the sentence as is without adding anything to it.

Examples:
- what furniture there is in my room? --> In my room there is a bed, a guardrobe and a desk with my computer
- where did you go today --> today I was at school
- I like ice cream --> I like ice cream
- how old is Jack --> Jack is 20 years old
- {input} -->
"""

    return hyde_prompt


@hook(priority=0)
def get_summarization_prompt(cat):
    summarization_prompt = """Write a concise summary of the following:
{text}
"""
    return summarization_prompt


@hook(priority=0)
def format_episodic_memories_for_prompt(memory_docs, cat):
    # convert docs to simple text
    memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

    # add time information (e.g. "2 days ago")
    memory_timestamps = []
    for m in memory_docs:
        timestamp = m[0].metadata["when"]
        delta = timedelta(seconds=(time.time() - timestamp))
        memory_timestamps.append(f" ({verbal_timedelta(delta)})")

    memory_texts = [a + b for a, b in zip(memory_texts, memory_timestamps)]

    memories_separator = "\n  - "
    memory_content = memories_separator + memories_separator.join(memory_texts)

    return memory_content


@hook(priority=0)
def format_declarative_memories_for_prompt(memory_docs, cat):
    # convert docs to simple text
    memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

    # add source information (e.g. "extracted from file.txt")
    memory_sources = []
    for m in memory_docs:
        source = m[0].metadata["source"]
        memory_sources.append(f" (extracted from {source})")

    memory_texts = [a + b for a, b in zip(memory_texts, memory_sources)]

    memories_separator = "\n  - "
    memory_content = memories_separator + memories_separator.join(memory_texts)

    return memory_content


@hook(priority=0)
def format_conversation_history_for_prompt(chat_history, cat):
    history = ""
    for turn in chat_history:
        history += f"\n - {turn['who']}: \"{turn['message']}\""

    return history
