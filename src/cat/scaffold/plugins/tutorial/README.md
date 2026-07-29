# Tutorial

A hands-on tour of the Cheshire Cat **agent model**. Two folders, each file an
idea — open them in any order.

```
tutorial/
├── agents/        # things you run
│   ├── hello_agent.py          prompt-only agent             (Poet)
│   ├── tool_agent.py           tools + a user-scoped db      (TodoAgent)
│   ├── time_aware_agent.py     attaching a directive         (TimeAwareAgent)
│   ├── introspective_agent.py  a tool with a guardrail       (IntrospectiveAgent)
│   └── mcp_agent.py            an MCP server as a directive   (MCPAgent)
└── directives/    # middleware that hooks the agent loop
    └── clock.py                the `clock` directive
```

## The mental model

> **An agent is a loop. Directives hook the loop. Tools are its hands.**

```
   ┌─────────────────────────── Agent.__call__(task) ───────────────────────────┐
   │                                                                             │
   │   start()  ──►  ┌──────────────── loop ────────────────┐  ──►  finish()     │
   │   directives    │  reset prompt                         │       directives   │
   │   .start()      │  directives .step()                   │       .finish()    │
   │                 │  llm(prompt, messages, tools)         │                    │
   │                 │  run any tool calls ──► repeat        │                    │
   │                 └───────────────────────────────────────┘                    │
   └─────────────────────────────────────────────────────────────────────────────┘
```

- **Agent** — *a verb you run*. A fresh instance per request holds its own
  `task`, `result`, `system_prompt` and `tools`. Define one by subclassing
  `Agent` in `agents/`, and the Cat registers it automatically by its `slug`.
- **Directive** — middleware with three lifecycle hooks (`start` / `step` /
  `finish`) that edits the agent in place. "RAG", "guardrails" and "memory" are
  not special features — they are all just directives. They live in `directives/`
  and agents attach them by slug.
- **Tool** — a method decorated with `@tool`. Its docstring and type hints are
  the manual the LLM reads. Tools belong to an agent; share them by inheritance,
  add them cross-cuttingly with a directive. There is no global tool pool.

## Talking to an agent

Send a streaming AG-UI request and name the agent by its `slug`:

```json
POST /agents/{slug}/message
{
  "threadId": "thread-1",
  "runId": "run-1",
  "state": {},
  "messages": [
    {
      "id": "message-1",
      "role": "user",
      "content": "add milk and eggs, then show my list"
    }
  ],
  "tools": [
    {
      "name": "confirm_action",
      "description": "Ask the user to confirm an action in the frontend.",
      "parameters": {
        "type": "object",
        "properties": {
          "message": { "type": "string" }
        },
        "required": ["message"]
      }
    }
  ],
  "context": [],
  "forwardedProps": {}
}
```

The response is an SSE stream of AG-UI events. For a non-streaming call, send
the internal `Task` format with `"stream": false`; a streaming `Task` is rejected
because native AG-UI clients select streaming by sending `RunAgentInput`.

Tools in `RunAgentInput.tools` belong to the requesting frontend. Cheshire Cat
offers their schemas to the model and emits `TOOL_CALL_START`, `TOOL_CALL_ARGS`
and `TOOL_CALL_END`, but never executes them on the server. The frontend executes
the selected tool and sends its result in the next run as a `ToolMessage` with
the matching `toolCallId`. Client tool names must not shadow agent or MCP tools.

The default agent is `default`. Any agent in any installed plugin can be
addressed by its `slug`.

