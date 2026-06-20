"""
Per-request ambient context (`cat.ambient.context_vars`).

Salvaged from the old `tests_giga` draft, ported to the v2 module layout. These
are deliberately self-contained — they drive asyncio directly and need no app.
"""

import asyncio

import pytest

from cat.ambient.context_vars import Ctx, ctx, use_ctx, user


def _user(name: str):
    from uuid import uuid5, NAMESPACE_DNS
    from cat.auth.user import User

    return User(id=uuid5(NAMESPACE_DNS, name), name=name)


def test_concurrent_requests_are_isolated():
    """Two interleaved tasks each observe their own user via the live proxy."""
    alice, bob = _user("alice"), _user("bob")
    seen: dict[str, str] = {}

    async def handler(label: str, u):
        with use_ctx(Ctx(user=u)):
            await asyncio.sleep(0)  # yield so the other task interleaves
            seen[label] = user.name
            await asyncio.sleep(0)
            assert user.name == u.name  # still ours after interleaving

    async def main():
        await asyncio.gather(handler("A", alice), handler("B", bob))

    asyncio.run(main())
    assert seen == {"A": "alice", "B": "bob"}


def test_user_outside_request_raises():
    """Reading the proxy with no active request raises a clear error."""

    async def main():
        with pytest.raises(RuntimeError, match="request"):
            _ = user.id

    asyncio.run(main())


def test_user_without_authenticated_user_raises():
    """A request context with no user still errors clearly on access."""

    async def main():
        with use_ctx(Ctx(user=None)):
            with pytest.raises(RuntimeError, match="user"):
                _ = user.name

    asyncio.run(main())


def test_ctx_resets_after_block():
    """Leaving a `use_ctx` block restores the empty context."""

    def ctx_is_empty() -> bool:
        try:
            ctx()
            return False
        except RuntimeError:
            return True

    async def main():
        assert ctx_is_empty()
        with use_ctx(Ctx(user=_user("alice"))):
            assert ctx().user.name == "alice"
        assert ctx_is_empty()

    asyncio.run(main())
