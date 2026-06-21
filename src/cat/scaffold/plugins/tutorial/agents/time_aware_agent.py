"""
An agent that uses a directive.

A directive is reusable middleware over the agent loop. This agent attaches the
`clock` directive (see `directives/clock.py`), which injects the current time on
every turn — so the agent always knows "now".

Directives are attached by listing them in `directives`. Here we reference the
directive by its **slug** (`"clock"`): the agent and the directive live in
different folders and never import each other. Core resolves the slug through the
registry at run time. (You could also pass a ready-made instance, e.g.
`directives = [ClockDirective()]`, when you want to configure it inline.)
"""

from cat import Agent


class TimeAwareAgent(Agent):
    slug = "time_aware"
    name = "Time-Aware Agent"
    description = "A helpful assistant that always knows the current date and time."

    # Attach the directive by its registered slug.
    directives = ["clock"]

    system_prompt = (
        "You are a helpful assistant. When the user asks about dates, times, "
        "schedules or 'how long until...', use the current time you were given."
    )
