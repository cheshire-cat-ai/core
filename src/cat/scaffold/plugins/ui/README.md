# Web UI

The multi-chat, multi-agent web frontend for the Cheshire Cat. This plugin is
**frontend-only**: it serves the built single-page app from `dist/` and an
`/assets/...` static route.

Conversation persistence is not its job — it talks to the [`chats`](../chats)
plugin over the `/api/v2/chats` REST API. There is no Python import from `ui`
into `chats`; either plugin can be removed or replaced independently.

## Contents

- `dist/` — the built web app (vendored at release time from the `ui` repo).
- `endpoints/frontend.py` — serves `dist/index.html` and `dist/assets/*`.

## Refreshing the build

The contents of `dist/` are produced by the `ui` repo's build. At release time,
CI refreshes this folder from that build — it is not edited by hand here.
