"""
A tool with a guardrail.

So far tools have been small and safe. But a tool is just a Python method, so it
can reach the whole machine — which means *you* decide what it is allowed to do.
The guardrail lives in the tool body: validate the input, then act (or refuse).

This agent has a single tool, `bash`, that runs a shell command — but only
read-only ones (grep, cat, head, tail, ls, find, wc). It runs them against the
Cheshire Cat's own source tree, so you can ask it to explain how the framework
works and watch it grep the code to find out:

    "how does the agentic loop decide when to stop?"
    -> it greps for the loop, reads `services/agents/base.py`, and explains.

Three things keep it safe, all visible below:
- an allow-list of programs — anything else is refused;
- a sandbox — paths must stay inside the framework source (no `/`, no `..`);
- commands are parsed with `shlex` and run WITHOUT a shell, so `;`, `|`, `>` and
  backticks are passed as literal arguments, never interpreted. (That also means
  pipes don't work — one command at a time.)
"""

import asyncio
import shlex
from pathlib import Path

import cat
from cat import Agent, tool


# The Cat's own package directory. The agent reads *these* files.
FRAMEWORK_ROOT = Path(cat.__file__).parent


class IntrospectiveAgent(Agent):
    slug = "introspective"
    name = "Introspective Agent"
    description = "Explores the Cheshire Cat's own source code with read-only shell commands."

    # The guardrail, as data. Read-only programs only — extend the set to open
    # the tool up.
    allowed_commands = {"grep", "cat", "head", "tail", "ls", "find", "wc"}

    system_prompt = (
        "You are an introspective agent: you answer questions about the Cheshire "
        "Cat framework by reading its own source code. Use `bash` to grep "
        "and read files — explore first, then explain what you actually found, "
        "quoting file paths. One command at a time; pipes are not supported."
    )

    @tool
    async def bash(self, command: str) -> str:
        """
        Run a single read-only shell command against the framework source and
        return its output. Examples: `grep -rn "class Agent" .`,
        `cat services/agents/base.py`. Pipes are not supported — run one command
        at a time.
        """
        parts = shlex.split(command)
        if not parts:
            return "Empty command."

        program = parts[0]
        if program not in self.allowed_commands:
            allowed = ", ".join(sorted(self.allowed_commands))
            return f"'{program}' is not allowed. Read-only commands only: {allowed}."

        # Sandbox: stay inside the framework tree — no absolute paths, no `..`.
        if any(arg.startswith("/") or ".." in arg.split("/") for arg in parts[1:]):
            return "Paths must stay inside the framework source (no '/' or '..')."

        proc = await asyncio.create_subprocess_exec(
            *parts,
            cwd=FRAMEWORK_ROOT,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
        except asyncio.TimeoutError:
            proc.kill()
            return "Command timed out."

        output = stdout.decode() or stderr.decode() or "(no output)"
        # Cap the result so a huge grep doesn't blow up the prompt.
        return output[:4000]
