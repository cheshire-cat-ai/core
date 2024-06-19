from os import getenv
from typing import Type
from pydantic import BaseModel, ConfigDict

from cat.log import log
from cat.mad_hatter.mad_hatter import MadHatter
from cat.factory.custom_auth_handler import (
    BaseAuthHandler,
    CoreAuthHandler,
    KeycloackAuthHandler,
    #, AuthEnvironmentVariables, AuthApiKey
)


class AuthHandlerConfig(BaseModel):
    _pyclass: Type[BaseAuthHandler] = None

    @classmethod
    def get_auth_handler_from_config(cls, config):
        if cls._pyclass is None or issubclass(cls._pyclass.default, BaseAuthHandler) is False:
            raise Exception(
                "AuthHandler configuration class has self._pyclass==None. Should be a valid AuthHandler class"
            )
        return cls._pyclass.default(**config)


class CoreAuthHandlerConfig(AuthHandlerConfig):
    _pyclass: Type = CoreAuthHandler

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Internal OAuth2 Handler",
            "description": "Yeeeeah.",
            "link": "",
        }
    )


class KeycloackAuthHandlerConfig(AuthHandlerConfig):
    _pyclass: Type = KeycloackAuthHandler

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Keycloak Auth Handler",
            "description": "Based on OpenID connect (OAuth2 dialect).",
            "link": "",
        }
    )

"""
class AuthEnvironmentVariablesConfig(AuthHandlerConfig):
    _pyclass: Type = AuthEnvironmentVariables

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "No AuthHandler",
            "description": "No auth_handler is used. All requests are allowed.",
            "link": "",
        }
    )

class AuthApiKeyConfig(AuthHandlerConfig):
    api_key_http: str
    api_key_ws: str
    _pyclass: Type = AuthApiKey

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "API Key AuthHandler",
            "description": 'Authorize requests based on API key',
            "link": "",
        }
    )
"""

def get_allowed_auth_handler_strategies():
    list_auth_handler_default = [
        CoreAuthHandlerConfig,
        KeycloackAuthHandlerConfig,
        #AuthEnvironmentVariablesConfig,
        #AuthApiKeyConfig,
    ]

    mad_hatter_instance = MadHatter()
    list_auth_handler = mad_hatter_instance.execute_hook(
        "factory_allowed_auth_handlers", list_auth_handler_default, cat=None
    )

    return list_auth_handler

def get_auth_handlers_schemas():
    AUTH_HANDLER_SCHEMAS = {}
    for config_class in get_allowed_auth_handler_strategies():
        schema = config_class.model_json_schema()
        schema["auhrizatorName"] = schema["title"]
        AUTH_HANDLER_SCHEMAS[schema["title"]] = schema
    
    return AUTH_HANDLER_SCHEMAS

def get_auth_handler_from_name(name):
    list_auth_handler = get_allowed_auth_handler_strategies()
    for auth_handler in list_auth_handler:
        if auth_handler.__name__ == name:
            return auth_handler
    return None