"""
Agents · 0 — A prompt-only agent.

The smallest possible agent: a name and a system prompt. No tools, no
directives. Subclass `Agent`, give it a `slug` (how clients address it) and a
`system_prompt` (its personality and instructions), and the Cat picks it up
automatically at startup.

Talk to it by sending a message with `{"agent": "haiku"}`.
"""

from cat import Agent


class HaikuBot(Agent):
    # `slug` is the id clients use in ChatRequest.agent. Keep it short.
    slug = "haiku"
    # `name` and `description` are shown in agent listings (e.g. the UI).
    name = "Haiku Bot"
    description = "Answers every message with a single haiku."

    # The system prompt is the agent's whole behaviour at this level.
    system_prompt = (
        "You are a poet living in Wonderland. "
        "Whatever the user says, you answer with a single haiku: "
        "three lines, 5-7-5 syllables. Never break character."
    )
