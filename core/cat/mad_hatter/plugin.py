


# this class represents a plugin in memory
# the plugin itsefl is managed as much as possible unix style
#      (i.e. by saving information in the folder itself)

class Plugin:

    def __init__(self, plugin_absolute_path):

        # where the plugin is on disk
        self.path: str = plugin_absolute_path

        # all plugins start inactive
        self.active: bool = False

        # plugin manifest

        # plugin settings

        # list of hooks

        # list of tools
