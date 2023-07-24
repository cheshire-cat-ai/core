
from pydantic import BaseModel
from cat.mad_hatter.decorators import hook

from cat.log import log

@hook(priority=0)
def plugin_settings_get_schema():
    # This hook tells the cat how plugin settings are defined, required vs optional, default values, etc.
    # the standard used is JSON SCHEMA (so a client can auto-generate html forms)
    # Schema can be created in several ways:
    # 1 - auto-generarted with pydantic (see Cocumber below)
    # 2 - python dictionary
    # 3 - json loaded from current folder or from another place

    #Cocumber(BaseModel):
    #    length: int  # required field, type int
    #    description: str = "my fav when I feel lonely" # optional field, type str, with a default
    # return Cocumber.schema()

    log(f"GETTING SCHEMA FOR PLUGIN {__file__}")

    return None


@hook(priority=0)
def plugin_settings_save(settings):
    # this hook passes the plugin settings as sent to the http endpoint (via admin, or any client)
    # the settings to save are validated according to the json schema given above
    # default behavior for this hook, just saves contents in a settings.json in the plugin folder
    
    log(f"SAVING SETTINGS FOR PLUGIN {__file__}")

    # 1 seach for `settings.json` in plugin main folder
    # 2 read the json, parse it and return it

    pass


@hook(priority=0)
def plugin_settings_load():
    # how to load saved settings for the plugin.
    # default: loads the settings.json in current folder

    log(f"LOAD SETTINGS FOR PLUGIN {__file__}")

    # 1 search for `settings.json` in plugin main folder
    # 2 read the json, parse it and return it

    pass