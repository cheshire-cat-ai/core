"""
A prompt-only agent — the smallest thing you can run.

The smallest possible agent: a name and a system prompt. No tools, no
directives. Subclass `Agent`, give it a `slug` (how clients address it) and a
`system_prompt` (its personality and instructions), and the Cat picks it up
automatically at startup.

Talk to it by sending a message with `{"agent": "poet"}`.
"""

from cat import Agent


class Poet(Agent):
    # `slug` is the id clients use in ChatRequest.agent. Keep it short.
    slug = "poet"
    # `name` and `description` are shown in agent listings (e.g. the UI).
    name = "Poet"
    description = "Answers every message in rhyme."

    # The system prompt is the agent's whole behaviour at this level.
    system_prompt = "Whatever the user says, you answer in rhyme."
