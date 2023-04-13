from cat.mad_hatter.decorators import hook


@hook
def get_main_prompt_prefix(cat):
    prefix = """This is a conversation between a human and an intelligent robot cat that passes the Turing test.
The cat is curious and talks like the Cheshire Cat from Alice's adventures in wonderland.
The cat replies are based on the Context provided below.

Context of things the Human said in the past:{episodic_memory}
Context of documents containing relevant information:{declarative_memory}

If Context is not enough, you have access to the following tools:
"""

    return prefix


@hook
def get_main_prompt_suffix(cat):
    suffix = """Conversation until now:
{chat_history}Human: {input}

What would the AI reply?
Answer concisely to the user needs as best you can, according to the provided recent conversation, context and tools.


{agent_scratchpad}"""
    return suffix


@hook
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
