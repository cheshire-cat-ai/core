"""
Agents · 1 — An agent with tools (its "hands").

A tool is a method on the agent decorated with `@tool`. Its name, docstring and
type hints become the schema the LLM sees, so write a clear docstring: that is
the tool's manual.

Watch the agentic loop work: ask "what is (3 + 4) * 5?" and the agent will call
`add(3, 4)`, see `7`, then call `multiply(7, 5)` — two turns of the loop, each a
real tool call — instead of guessing the arithmetic in its head.

Tools are *agent-scoped*: this agent sees exactly the tools defined on it (plus
any MCP tools). To share tools across agents, put them on a mixin and inherit it;
to add tools cross-cuttingly, use a directive.
"""

from cat import Agent, tool


class CalculatorAgent(Agent):
    slug = "calculator"
    name = "Calculator Agent"
    description = "A precise calculator that uses tools for every arithmetic step."

    system_prompt = (
        "You are a meticulous calculator. You are bad at mental arithmetic and "
        "you know it, so you ALWAYS use your tools for every single operation, "
        "one step at a time. Never compute a result yourself. "
        "When you have the final number, state it plainly."
    )

    @tool
    def add(self, a: float, b: float) -> str:
        """Add two numbers together and return the sum."""
        return str(a + b)

    @tool
    def multiply(self, a: float, b: float) -> str:
        """Multiply two numbers together and return the product."""
        return str(a * b)
