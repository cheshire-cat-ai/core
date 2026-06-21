# Contributing to Cheshire Cat

Few simple rules:

- propose changes via issue or reply to an existing issue
- only send a PR if you have an assigned issue
- send PR directly on branch `main` or on a feature branch
- ok for AI written code, but consider I need to read it, so keep it well commented, well tested, and concise

## Dev setup

  ```bash
  git clone ....
  cd core
  uv venv
  uv run ccat
  ```

  To run linter and tests
  ```bash
  uv run ruff check
  uv run pytest
  ```
