# Chats

Conversation persistence for the Cat. This plugin owns:

- the `ccat_chats` table (`db.py`), built on core's `UserScopedDB` so every
  conversation is scoped to its owner;
- the `/api/v2/chats` REST CRUD (`endpoints/crud.py`), built with the generic
  `create_crud` helper.

It is **backend-only** — no frontend, no vendor dependencies. The `ui` plugin (or
any other frontend, or a headless integration) reaches saved conversations over
this REST API, so `chats` is useful on its own and deletable independently of
`ui`.

## API

| Method | Path                  | Description           |
| ------ | --------------------- | --------------------- |
| GET    | `/api/v2/chats`       | list / search chats   |
| GET    | `/api/v2/chats/{id}`  | get one chat          |
| POST   | `/api/v2/chats`       | create a chat         |
| PUT    | `/api/v2/chats/{id}`  | update a chat         |
| DELETE | `/api/v2/chats/{id}`  | delete a chat         |

All routes are restricted to the calling user's own chats.
