from pydantic import BaseModel
from cat.mad_hatter.decorators import plugin


class MockPluginSettings(BaseModel):
    a: str = "a"
    b: int


@plugin
def settings_schema():
    return MockPluginSettings.model_json_schema()


@plugin
def settings_model():
    return MockPluginSettings


# TODO: test custom settings load
#@plugin
#def load_settings():
#    return {}


# TODO: test custom settings save
#@plugin
#def save_settings(settings):
#    return {}


@plugin
def activated(plugin):
    plugin.custom_activation_executed = True


@plugin
def deactivated(plugin):
    plugin.custom_deactivation_executed = True
