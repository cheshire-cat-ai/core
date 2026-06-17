from typing import Union, Literal, Type, Any, Dict, List, TYPE_CHECKING
from pydantic import BaseModel, ValidationError

if TYPE_CHECKING:
    from fastapi import Request
    from cat.looking_glass.cheshire_cat import CheshireCat
    from cat.auth.user import User
    from cat.mad_hatter.plugin import Plugin
    from cat.protocols.model_context.client import MCPClients

LifeCycle = Literal["singleton", "request"]

class Service:
    """
    Base class for plugin defined services.
    Do not subclass this directly - use SingletonService or RequestService instead.
    """

    service_type: str = "base"
    lifecycle: LifeCycle | None = None
    slug: str | None = None
    name: str | None = None
    description: str | None = None
    plugin_id: str | None = None

    requires: Dict[str, Union[str, List[str]]] = {}
    """
    Static dependency declarations resolved by ServiceFactory before setup().
    Keys are service_type strings; values are a slug or list of slugs.
    Each resolved instance is injected as self.<service_type>.
    """

    ccat: "CheshireCat"

    @property
    def plugin(self) -> Union["Plugin", None]:
        """Access to the Plugin that provided this service, if any."""
        if self.plugin_id is None:
            return None
        return self.ccat.mad_hatter.plugins[self.plugin_id]

    @property
    def mcp_clients(self) -> "MCPClients":
        """Access to MCP clients."""
        return self.ccat.mcp_clients

    async def setup(self) -> None:
        """
        Async setup for the service (e.g. load API keys from settings).
        Override in subclasses.
        """
        pass

    async def teardown(self) -> None:
        """
        Async cleanup for the service (e.g. close connections, cleanup resources).
        Called during shutdown for singleton services.
        Override in subclasses if cleanup is needed.
        """
        pass

    async def execute_hook(self, hook_name: str, default_value: Any) -> Any:
        """
        Execute a hook for plugins to be intercepted.

        Parameters
        ----------
        hook_name : str
            Name of the hook to execute.
        default_value : Any
            Default value if hook doesn't modify it.

        Returns
        -------
        Any
            The value after hook execution.
        """
        return await self.ccat.mad_hatter.execute_hook(
            hook_name,
            default_value,
            caller=self
        )

    async def settings_model(self) -> Type[BaseModel] | None:
        """
        Return the Pydantic model for service settings.
        Override in subclasses to provide dynamic settings schemas.

        By default, returns the nested `Settings` class if one is declared
        on the service class. Override this method to provide dynamic schemas
        (e.g., schemas that depend on installed plugins). When both a nested
        `Settings` class and a `settings_model()` override exist, the override
        takes precedence.

        Returns
        -------
        Type[BaseModel] | None
            Pydantic BaseModel class, or None if no settings.

        Example
        -------
        ```python
        from pydantic import BaseModel

        class MyService(SingletonService):
            # Preferred: nested Settings class
            class Settings(BaseModel):
                api_key: str
                timeout: int = 30

            # OR: override settings_model() for dynamic schemas
            async def settings_model(self):
                class DynamicSettings(BaseModel):
                    api_key: str
                return DynamicSettings
        ```
        """
        # Default: return nested Settings class if declared
        nested = getattr(self.__class__, 'Settings', None)
        if nested is not None and isinstance(nested, type) and issubclass(nested, BaseModel):
            return nested
        return None

    @classmethod
    def _settings_db_key(cls) -> str:
        """DB key for this service's settings: settings_{plugin_id}_{service_type}_{slug}."""
        return f"settings_{cls.plugin_id}_{cls.service_type}_{cls.slug}"

    async def load_settings(self) -> BaseModel | None:
        """
        Load service settings from KeyValueDB (installation-wide).
        Returns a typed Pydantic model instance, or None if no settings model is defined.
        No side effects on self.

        Returns
        -------
        BaseModel | None
            Validated settings model instance (with DB values or defaults), or None.
        """
        from cat.db import DB

        model = await self.settings_model()
        if model is None:
            return None

        raw = await DB.load(self._settings_db_key())
        if raw is None:
            return model()

        try:
            return model.model_validate(raw)
        except ValidationError:
            await DB.delete(self._settings_db_key())
            return model()

    async def save_settings(self, settings: BaseModel | dict) -> BaseModel | None:
        """
        Save service settings to KeyValueDB (installation-wide).
        Validates payload against the settings model, persists to DB, returns the model instance.
        No side effects on self.

        Parameters
        ----------
        settings : BaseModel | dict
            The complete settings to save for this service.

        Returns
        -------
        BaseModel | None
            Validated settings model instance, or None if no settings model is defined.
        """
        from cat.db import DB

        model = await self.settings_model()
        if model is None:
            return None

        if isinstance(settings, dict):
            validated = model.model_validate(settings)
        else:
            validated = settings

        await DB.save(self._settings_db_key(), validated.model_dump())
        return validated



class SingletonService(Service):
    """
    Base class for singleton services (Auth, ModelProvider, Memory).

    Global services are instantiated once during CheshireCat bootstrap
    and reused across all requests.

    Settings are persisted installation-wide in KeyValueDB.
    """

    lifecycle = "singleton"


class RequestService(Service):
    """
    Base class for request-scoped services (e.g. Agent).
    Request services are instantiated fresh for each request and related to a specific user.

    Settings are persisted installation-wide in KeyValueDB (admin-configured defaults).
    """

    lifecycle = "request"
    request: "Request"

    @property
    def user(self) -> "User":
        """Access the current user from request state."""
        return self.request.state.user

    @property
    def user_id(self) -> str:
        """Get the current user ID."""
        return self.user.id
