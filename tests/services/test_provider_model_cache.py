"""Model-discovery caching on the provider singleton.

The contract under test (the thing that's annoying to verify by hand):

- `list_models()` is the cached entry point: discovery is a network round-trip,
  so the result is cached on the singleton *instance*.
- A non-empty result sticks; an empty/failed one does NOT (so a local server
  that wasn't up yet retries instead of being pinned empty).
- `refresh()` — what the settings endpoint calls after a save — drops the
  singleton, and with it the cache, so the next call re-discovers.

We never hit the network: a tiny subclass overrides the single seam
`fetch_models()` (the raw vendor call) with a call counter. Testing the
base-class contract on a throwaway subclass also keeps the real provider
singletons unpolluted.
"""

import pytest

from cat.base import OpenAICompatibleProvider


def make_provider(models, slug="cache_probe"):
    """A provider whose discovery is a counter, not a network call.

    `count` lets each test assert how many times the real (uncached) discovery
    actually ran. A fresh subclass per call means a fresh singleton cache.
    """

    class Probe(OpenAICompatibleProvider):
        pass

    Probe.slug = slug
    Probe.count = 0

    async def _fetch(self):
        Probe.count += 1
        return list(models)

    Probe.fetch_models = _fetch
    return Probe


@pytest.mark.asyncio
async def test_fetch_is_cached_across_calls():
    Probe = make_provider(["gpt-4", "text-embedding-3-small"])
    p = Probe()

    assert await p.list_models() == ["gpt-4", "text-embedding-3-small"]
    await p.list_models()
    await p.list_models()

    # one real discovery, the rest served from the instance cache
    assert Probe.count == 1


@pytest.mark.asyncio
async def test_list_llms_and_embedders_share_one_fetch():
    # the old double-fetch bug: list_llms + list_embedders each hit the network
    Probe = make_provider(["gpt-4", "text-embedding-3-small"])
    p = Probe()

    assert await p.list_llms() == ["gpt-4"]
    assert await p.list_embedders() == ["text-embedding-3-small"]

    assert Probe.count == 1


@pytest.mark.asyncio
async def test_empty_result_is_not_cached():
    # a server that wasn't reachable yet must retry, not stay pinned empty
    Probe = make_provider([])
    p = Probe()

    await p.list_models()
    await p.list_models()

    assert Probe.count == 2


@pytest.mark.asyncio
async def test_refresh_invalidates_cache():
    # refresh() is what the settings endpoint calls after a save: it drops the
    # singleton (and the cache), so the next resolution re-discovers.
    Probe = make_provider(["gpt-4"])

    assert await Probe().list_models() == ["gpt-4"]
    assert Probe.count == 1

    await Probe.refresh()  # settings changed → drop singleton

    assert await Probe().list_models() == ["gpt-4"]
    assert Probe.count == 2  # re-discovered with (hypothetically) new settings


@pytest.mark.asyncio
async def test_same_singleton_shares_cache():
    # two resolutions of the same class are the SAME object → same cache
    Probe = make_provider(["gpt-4"])

    a = Probe()
    b = Probe()
    assert a is b

    await a.list_models()
    await b.list_models()
    assert Probe.count == 1
