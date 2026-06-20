"""
The single CheshireCat instance per process.

`ccat()` returns the one running instance; `set_ccat()` registers it once at
bootstrap (see `CheshireCat.bootstrap`). A plain module global, not a contextvar
— there is exactly one cat per process, shared by every request.

Internal plumbing behind the `cat` package front door: user code never names
`ccat()`, it reaches ambient state with `from cat import ...`. The per-request
context lives in `cat.ambient.context_vars`.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cat.looking_glass.cheshire_cat import CheshireCat


_ccat: "CheshireCat | None" = None


def ccat() -> "CheshireCat":
    """Return the one CheshireCat instance. Internal usage only."""
    if _ccat is None:
        raise RuntimeError("CheshireCat is not bootstrapped yet.")
    return _ccat


def set_ccat(instance: "CheshireCat") -> None:
    """Register the process-wide CheshireCat instance (called at bootstrap)."""
    global _ccat
    _ccat = instance


class _PluginProxy:
    """Live proxy to the plugin that owns the calling code.

    `from cat import plugin` binds this once; every attribute read resolves the
    plugin of whatever code is currently executing (matched by call-stack file
    path). Lets plugin code reach its own metadata/path — `plugin.path` — without
    importing the cat handle or threading `self`.
    """

    def _plugin(self):
        return ccat().plugin

    def __getattr__(self, name):
        return getattr(self._plugin(), name)

    def __repr__(self):
        return "<cat.plugin (current)>"


plugin = _PluginProxy()
