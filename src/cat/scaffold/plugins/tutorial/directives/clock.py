"""
Directives · clock — make any agent time-aware.

A directive hooks the three moments of an agent's life:

    start(agent)   once, before the loop      -> setup: filter tools, set base prompt
    step(agent)    every turn, before the LLM  -> per-turn context: RAG, guardrails, clock
    finish(agent)  once, after the loop        -> teardown: save memory, log, audit

A directive receives the live `agent` and edits it in place. The loop resets the
system prompt before each `step()`, so anything appended here is fresh every turn
(never accumulated).

`ClockDirective` is registered by its `slug` ("clock"), so any agent can attach
it with `directives = ["clock"]` without importing this file.
"""

from datetime import datetime

from cat import Directive, Agent


class ClockDirective(Directive):
    slug = "clock"
    name = "Clock"
    description = "Injects the current date and time into the prompt each turn."

    async def step(self, agent: Agent) -> None:
        now = datetime.now().strftime("%A %d %B %Y, %H:%M")
        agent.system_prompt += f"\n\nThe current date and time is: {now}."
