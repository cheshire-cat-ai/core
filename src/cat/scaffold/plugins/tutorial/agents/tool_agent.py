"""
An agent with tools (its "hands") that touch a real database.

A tool is a method on the agent decorated with `@tool`. Its name, docstring and
type hints become the schema the LLM sees, so write a clear docstring: that is
the tool's manual. Tools can be `async`, so they can `await` the database, the
network, anything.

This agent keeps a personal to-do list. Watch the agentic loop work: say
"add milk and eggs, then show my list" and the agent will call `create_todo`
twice and then `list_todos` — several turns of the loop, each a real tool call —
before answering.

The list is **scoped to the caller**: every read and write goes through
`from cat import user`, the ambient handle to whoever sent the message. Two
users talking to the same agent never see each other's todos — you never pass a
user id around, `user` already *is* the caller.

Tools are *agent-scoped*: this agent sees exactly the tools defined on it (plus
any MCP tools). To share tools across agents, put them on a mixin and inherit it;
to add tools cross-cuttingly, use a directive.
"""

from cat import Agent, tool, user


class TodoAgent(Agent):
    slug = "todo"
    name = "Todo Agent"
    description = "Keeps a personal to-do list, saved per user in the database."

    system_prompt = (
        "You are a friendly to-do list assistant. Use your tools to read and "
        "change the user's list — never invent items or pretend to remember "
        "them yourself. After changing the list, briefly confirm what you did. "
        "Each todo has a numeric id; use it to update or delete the right one."
    )

    # The whole list lives under a single user-scoped key, "todos". Every tool
    # below reads it with `user.load`, changes it, and writes it back with
    # `user.save` — scoped to the caller, no user id ever passed around.
    @tool
    async def list_todos(self) -> str:
        """List all of the user's todos with their id and done/not-done state."""
        
        todos = await user.load("todos", [])
        if not todos:
            return "The to-do list is empty."
        return "\n".join(
            f"[{'x' if t['done'] else ' '}] #{t['id']} {t['text']}"
            for t in todos
        )

    @tool
    async def create_todo(self, text: str) -> str:
        """Add a new todo with the given text. Returns the created item's id."""
        
        todos = await user.load("todos", [])
        new_id = max((t["id"] for t in todos), default=0) + 1
        todos.append({"id": new_id, "text": text, "done": False})
        await user.save("todos", todos)
        return f"Created todo #{new_id}: {text}"

    @tool
    async def update_todo(self, todo_id: int, text: str = "", done: bool = False) -> str:
        """Update a todo by id: change its text and/or mark it done."""

        todos = await user.load("todos", [])
        for t in todos:
            if t["id"] == todo_id:
                if text:
                    t["text"] = text
                t["done"] = done
                await user.save("todos", todos)
                return f"Updated todo #{todo_id}."
        return f"No todo with id #{todo_id}."

    @tool
    async def delete_todo(self, todo_id: int) -> str:
        """Delete a todo by id."""

        todos = await user.load("todos", [])
        kept = [t for t in todos if t["id"] != todo_id]
        if len(kept) == len(todos):
            return f"No todo with id #{todo_id}."
        await user.save("todos", kept)
        return f"Deleted todo #{todo_id}."
