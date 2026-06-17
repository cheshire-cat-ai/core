from pydantic import BaseModel


class PluginManifest(BaseModel):
    name: str
    version: str = "0.0.0"
    thumb: str = None
    tags: str = "Unknown"
    description: str = (
        "Description not found for this plugin."
        "Please create a plugin.json manifest"
        " in the plugin folder."
    )
    author_name: str = "Unknown"
    author_url: str = "Unknown"
    plugin_url: str = "Unknown"
    min_cat_version: str = "Unknown"
    max_cat_version: str = "Unknown"

