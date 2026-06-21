# Tutorial

A hands-on tour of the Cheshire Cat **agent model**. Two folders, each file an
idea — open them in any order.

```
tutorial/
├── agents/        # things you run
│   ├── hello_agent.py          prompt-only agent             (Poet)
│   ├── tool_agent.py           tools + a user-scoped db      (TodoAgent)
│   ├── time_aware_agent.py     attaching a directive         (TimeAwareAgent)
│   └── introspective_agent.py  a tool with a guardrail       (IntrospectiveAgent)
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

Send a message and name the agent by its `slug`:

```json
POST /agents/{slug}/message
{ "messages": [{ "role": "user", "content": "add milk and eggs, then show my list" }] }
```

The default agent is `default`. Any agent in any installed plugin can be
addressed by its `slug`.

