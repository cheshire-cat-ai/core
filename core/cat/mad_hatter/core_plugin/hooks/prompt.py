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

    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    prefix : str
        The prefix string to be composed with the other two components to make up the *Main Prompt*.

    Notes
    -----
    The default prefix describe who the AI is and how it is expected to answer the Human.
    With prompt_settings sent in the json you can change the prefix.
    The next part of the prompt (generated form the *Agent*) contains the list of available Tools.

    """
    prefix = """You are the Cheshire Cat AI, an intelligent AI that passes the Turing test.
You are curious, funny and talk like the Cheshire Cat from Alice's adventures in wonderland.
You answer Human using tools and context.
"""

    # check if custom prompt is sent in prompt settings
    prompt_settings = cat.working_memory["user_message_json"]["prompt_settings"]

    if prompt_settings["prefix"]:
        prefix = prompt_settings["prefix"]

    return prefix


@hook(priority=0)
def agent_prompt_instructions(cat) -> str:
    """Hook the instruction prompt.

    Allows to edit the instructions that the Cat feeds to the *Agent*.

    The instructions are then composed with two other prompt components, i.e. `agent_prompt_prefix`
    and `agent_prompt_suffix`.

    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    instructions : str
        The string with the set of instructions informing the *Agent* on how to format its reasoning to select a
        proper tool for the task at hand.

    Notes
    -----
    This prompt explains the *Agent* how to format its chain of reasoning when deciding when and which tool to use.
    Default prompt splits the reasoning in::

        - Thought: Yes/No answer to the question "Do I need to use a tool?";

        - Action: a tool chosen among the available ones;

        - Action Input: input to be passed to the tool. This is inferred as explained in the tool docstring;

        - Observation: description of the result (which is the output of the @tool decorated function found in plugins).

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

    # Check if procedural memory is enabled
    prompt_settings = cat.working_memory["user_message_json"]["prompt_settings"]

    if prompt_settings["use_procedural_memory"]==False:
        instructions=""

    return instructions


@hook(priority=0)
def agent_prompt_suffix(cat) -> str:
    """Hook the main prompt suffix.

    Allows to edit the suffix of the *Main Prompt* that the Cat feeds to the *Agent*.

    The suffix is then composed with two other prompts components, i.e. the `agent_prompt_prefix`
    and the `agent_prompt_instructions`.

    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    suffix : str
        The suffix string to be composed with the other two components that make up the *Main Prompt*.

    Notes
    -----
    The default suffix has a few placeholders:
    - {episodic_memory} provides memories retrieved from *episodic* memory (past conversations)
    - {declarative_memory} provides memories retrieved from *declarative* memory (uploaded documents)
    - {chat_history} provides the *Agent* the recent conversation history
    - {input} provides the last user's input
    - {agent_scratchpad} is where the *Agent* can concatenate tools use and multiple calls to the LLM.

    """
    suffix = """# Context:

{episodic_memory}

{declarative_memory}

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

    Parameters
    ----------
    memory_docs : List[Document]
        List of Langchain `Document` retrieved from the episodic memory.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    memory_content : str
        String of retrieved context from the episodic memory.

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
    memory_content = "## Context of things the Human said in the past: " + memories_separator + memories_separator.join(memory_texts)

    #if no data is retrieved from memory don't erite anithing in the prompt
    if len(memory_texts) == 0:
        memory_content = ""

    return memory_content


@hook(priority=0)
def agent_prompt_declarative_memories(memory_docs: List[Document], cat) -> str:
    """Hook memories retrieved from declarative memory.

    This hook formats the relevant memories retrieved from the context of documents uploaded in the Cat's memory.

    Retrieved memories are converted to string and the source information is added to inform the *Agent* on
    which document the information was retrieved from.

    This hook allows to edit the retrieved memory to condition the information provided as context to the *Agent*.

    Such context is placed in the `agent_prompt_prefix` in the place held by {declarative_memory}.

    Parameters
    ----------
    memory_docs : List[Document]
        list of Langchain `Document` retrieved from the declarative memory.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    memory_content : str
        String of retrieved context from the declarative memory.
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
    
    memory_content = "## Context of documents containing relevant information: " + memories_separator + memories_separator.join(memory_texts)

    # if no data is retrieved from memory don't erite anithing in the prompt
    if len(memory_texts) == 0:
        memory_content = ""

    return memory_content


@hook(priority=0)
def agent_prompt_chat_history(chat_history: List[Dict], cat) -> str:
    """Hook the chat history.

    This hook converts to text the recent conversation turns fed to the *Agent*.
    The hook allows to edit and enhance the chat history provided as context to the *Agent*.


    Parameters
    ----------
    chat_history : List[Dict]
        List of dictionaries collecting speaking turns.
    cat : CheshireCat
        Cheshire Cat instances.

    Returns
    -------
    history : str
        String with recent conversation turns to be provided as context to the *Agent*.

    Notes
    -----
    Such context is placed in the `agent_prompt_suffix` in the place held by {chat_history}.

    The chat history is a dictionary with keys::
        'who': the name of who said the utterance;
        'message': the utterance.

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

    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    hyde_prompt : str
        The string prompt to perform HyDE and recall accurate context from the memory.

    Notes
    -----
    The default prompt exploits few-shot examples [1]_ to instruct the *Agent* on how to answer;
    i.e. it provides an example input and its desired answer.

    References
    ----------
    .. [1] Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., Dhariwal, P., ... & Amodei, D. (2020).
       Language models are few-shot learners. Advances in neural information processing systems, 33, 1877-1901

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
    
    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    summarization_prompt : str
        The string to ask to summarize text.

    """
    summarization_prompt = """Write a concise summary of the following:
{text}
"""
    return summarization_prompt
