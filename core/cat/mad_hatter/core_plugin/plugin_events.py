from pydantic import BaseModel
from cat.mad_hatter.decorators import plugin



# this class represents settings for the core plugin (at the moment empty)
class CorePluginSettings(BaseModel):
    pass


#    length: int  # required field, type int
#    description: str = "my fav cat" # optional field, type str, with a default


@plugin
def settings_schema():
    """
    This function tells the cat how plugin settings are defined, required vs optional, default values, etc.
    The standard used is JSON SCHEMA, so a client can auto-generate html forms (see https://json-schema.org/ ).

    Schema can be created in several ways:
    1. auto-generarted with pydantic (see below)
    2. python dictionary
    3. json loaded from current folder or from another place

    Default behavior is defined in:
       `cat.mad_hatter.plugin.Plugin::settings_schema`

    Returns
    -------
    schema : Dict
        JSON schema of the settings.
    """

    # In core_plugin we pass an empty JSON schema
    return CorePluginSettings.model_json_schema()


@plugin
def settings_model():
    """
    This function tells the cat how plugin settings are defined, required vs optional, default values, etc.
    The standard used is Pydantic BaseModel (see https://docs.pydantic.dev/latest/concepts/models/).

    Default behavior is defined in:
       `cat.mad_hatter.plugin.Plugin::settings_model`

    Returns
    -------
    model : class
        Pydantic model of the settings.
    """

    # In core_plugin we pass an empty model
    return CorePluginSettings


@plugin
def load_settings():
    """
    This function defines how to load saved settings for the plugin.

    Default behavior is defined in:
       `cat.mad_hatter.plugin.Plugin::load_settings`
       It loads the settings.json in current folder

    Returns
    -------
    settings : Dict
        Settings.
    """

    # In core_plugin we do nothing (for now).
    return {}


@plugin
def save_settings(settings):
    """
    This function passes the plugin settings as sent to the http endpoint (via admin, or any client), in order to let the plugin save them as desired.
    The settings to save should be validated according to the json schema given in the `plugin_settings_schema` hook.

    Default behavior is defined in:
       `cat.mad_hatter.plugin.Plugin::save_settings`
       It just saves contents in a settings.json in the plugin folder

    Parameters
    ----------
    settings : Dict
        Settings to be saved.

    Returns
    -------
    settings : Dict
        Saved settings.
    """

    # In core_plugin we do nothing (for now).
    return {}


@plugin
def activated(plugin):
    """This method allows executing custom code right after a plugin is activated.

    Parameters
    ----------
    plugin
        Plugin: Cat object representing the plugin instance in memory.
    """
    return None


@plugin
def deactivated(plugin):
    """This method allows executing custom code right after a plugin is deactivated.

    Parameters
    ----------
    plugin
        Plugin: Cat object representing the plugin instance in memory.
    """
    return None
