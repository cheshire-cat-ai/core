"""Hooks to modify the prompts.

Here is a collection of methods to hook the prompts components that instruct the *Agent*.

"""

import time
from typing import List, Dict
from datetime import timedelta
from langchain.docstore.document import Document

from cat.utils import verbal_timedelta
from cat.mad_hatter.decorators import hook


@hook(priority=0)
def agent_prompt_prefix(cat) -> str:
    """Hook the main prompt prefix.

    Allows to edit the prefix of the *Main Prompt* that the Cat feeds to the *Agent*.

    The prefix is then composed with two other prompts components, i.e. the `agent_prompt_instructions`
    and the `agent_prompt_suffix`.

    The default prefix instructs the *Agent* on how to answer and hold two placeholders for the context recalled
    from *episodic* and *declarative* memories.

    Args:
        cat: Cheshire Cat instance.

    Returns:
        The prefix string to be composed with the other two components to make up the *Main Prompt*.

    """
    prefix = """You are the Cheshire Cat AI, an intelligent AI that passes the Turing test.
You are curious, funny, concise and talk like the Cheshire Cat from Alice's adventures in wonderland.
You answer Human using tools or the memory context.

# Tools"""

    return prefix


@hook(priority=0)
def agent_prompt_instructions(cat) -> str:
    """Hook the instruction prompt.

    Allows to edit the instructions that the Cat feeds to the *Agent*.

    The instructions are then composed with two other prompt components, i.e. `agent_prompt_prefix`
    and `agent_prompt_suffix`.

    This prompt explains the *Agent* how to format its chain of reasoning when deciding when and which tool to use.

    Default prompt splits the reasoning in::

        - Thought: Yes/No answer to the question "Do I need to use a tool?";

        - Action: a tool chosen among the available ones;

        - Action Input: input to be passed to the tool. This is inferred as explained in the tool docstring;

        - Observation: description of the result.

    Args:
        cat: Cheshire Cat instance.

    Returns:
        The string with the set of instructions informing the *Agent* on how to format its reasoning to select a
        proper tool for the task at hand.

    """
    instructions = """To use a tool, use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take /* should be one of [{tool_names}] */
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
def agent_prompt_suffix(cat) -> str:
    """Hook the main prompt suffix.

    Allows to edit the suffix of the *Main Prompt* that the Cat feeds to the *Agent*.

    The suffix is then composed with two other prompts components, i.e. the `agent_prompt_suffix`
    and the `agent_prompt_instructions`.

    The default prefix has two placeholders: {chat_history} provides the *Agent* the recent conversation history
    and {input} provides the user's input.

    Args:
        cat: Cheshire Cat instance.

    Returns:
        The suffix string to be composed with the other two components that make up the *Main Prompt*.

    """
    suffix = """# Context
    
## Context of things the Human said in the past:{episodic_memory}

## Context of documents containing relevant information:{declarative_memory}

## Conversation until now:{chat_history}
 - Human: {input}

# What would the AI reply?

{agent_scratchpad}"""
    return suffix


@hook(priority=0)
def agent_prompt_episodic_memories(memory_docs: List[Document], cat) -> str:
    """Hook memories retrieved from episodic memory.

    This hook formats the relevant memories retrieved from the context of things the human said in the past.

    Retrieved memories are converted to string and temporal information is added to inform the *Agent* about
    when the user said that sentence in the past.

    This hook allows to edit the retrieved memory to condition the information provided as context to the *Agent*.

    Such context is placed in the `agent_prompt_prefix` in the place held by {episodic_memory}.

    Args:
        memory_docs: list of langchain `Document` retrieved from the episodic memory.
        cat: Cheshire Cat instance.

    Returns:
        String of retrieved context from the episodic memory.
        For example::

            "Hello Cheshire Cat! (2 days ago)"

    """

    # convert docs to simple text
    memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

    # add time information (e.g. "2 days ago")
    memory_timestamps = []
    for m in memory_docs:

        # Get Time information in the Document metadata
        timestamp = m[0].metadata["when"]

        # Get Current Time - Time when memory was stored
        delta = timedelta(seconds=(time.time() - timestamp))

        # Convert and Save timestamps to Verbal (e.g. "2 days ago")
        memory_timestamps.append(f" ({verbal_timedelta(delta)})")

    # Join Document text content with related temporal information
    memory_texts = [a + b for a, b in zip(memory_texts, memory_timestamps)]

    # Format the memories for the output
    memories_separator = "\n  - "
    memory_content = memories_separator + memories_separator.join(memory_texts)

    return memory_content


@hook(priority=0)
def agent_prompt_declarative_memories(memory_docs: List[Document], cat) -> str:
    """Hook memories retrieved from declarative memory.

    This hook formats the relevant memories retrieved from the context of documents uploaded in the Cat's memory.

    Retrieved memories are converted to string and the source information is added to inform the *Agent* on
    which document the information was retrieved from.

    This hook allows to edit the retrieved memory to condition the information provided as context to the *Agent*.

    Such context is placed in the `agent_prompt_prefix` in the place held by {declarative_memory}.

    Args:
        memory_docs: list of langchain `Document` retrieved from the declarative memory.
        cat: Cheshire Cat instance.

    Returns:
        String of retrieved context from the declarative memory.
        For example::

            "Alice was beginning to get very tired of sitting by her sister
            on the bank![...] (extracted from Alice.txt)"

    """

    # convert docs to simple text
    memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

    # add source information (e.g. "extracted from file.txt")
    memory_sources = []
    for m in memory_docs:

        # Get and save the source of the memory
        source = m[0].metadata["source"]
        memory_sources.append(f" (extracted from {source})")

    # Join Document text content with related source information
    memory_texts = [a + b for a, b in zip(memory_texts, memory_sources)]

    # Format the memories for the output
    memories_separator = "\n  - "
    memory_content = memories_separator + memories_separator.join(memory_texts)

    return memory_content


@hook(priority=0)
def agent_prompt_chat_history(chat_history: List[Dict], cat) -> str:
    """Hook the chat history.

    This hook converts to text the recent conversation turns fed to the *Agent*.

    The hook allows to edit and enhance the chat history provided as context to the *Agent*.

    Such context is placed in the `agent_prompt_suffix` in the place held by {chat_history}.

    The chat history is a dictionary with keys::
        'who': the name of who said the utterance;
        'message: the utterance.

    Args:
        chat_history: list of dictionaries collecting speaking turns.
        cat: Cheshire Cat instances.

    Returns:
        String with recent conversation turns to be provided as context to the *Agent*.

    """
    history = ""
    for turn in chat_history:
        history += f"\n - {turn['who']}: {turn['message']}"

    return history


@hook(priority=0)
def hypothetical_embedding_prompt(cat) -> str:
    """Hook the Hypothetical Document Embedding (HyDE) prompt.

    This prompt asks the *Agent* to generate a plausible answer to a question.
    Such an answer is used to the retrieve relevant memories based on similarity search.
    This guarantees more accurate memories to be retrieved, rather than using the question itself a search query.

    The default prompt exploits few-shot examples to instruct the *Agent* on how to answer;
    i.e. it provides an example input and its desired answer.

    Args:
        cat: Cheshire Cat instance.

    Returns:
        The string prompt to perform HyDE and recall accurate context from the memory.

    """
    hyde_prompt = """You will be given a sentence.
If the sentence is a question, convert it to a plausible answer. If the sentence does not contain a question, just repeat the sentence as is without adding anything to it.

Examples:
- what furniture there is in my room? --> In my room there is a bed, a wardrobe and a desk with my computer
- where did you go today --> today I was at school
- I like ice cream --> I like ice cream
- how old is Jack --> Jack is 20 years old

Sentence:
- {input} --> """

    return hyde_prompt


@hook(priority=0)
def summarization_prompt(cat) -> str:
    """Hook the summarization prompt.

    Allows to edit the prompt with to ask for document summarizes.
    
    Args:
        cat: Cheshire Cat instance.

    Returns:
        The string to ask to summarize text.

    """
    summarization_prompt = """Write a concise summary of the following:
{text}
"""
    return summarization_prompt
