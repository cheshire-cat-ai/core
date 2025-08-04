import os
import glob
import shutil

from cat.db.cruds import settings as crud_settings
from cat.db.database import DEFAULT_SYSTEM_KEY
from cat.db.models import Setting
from cat.log import log
from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.plugin_extractor import PluginExtractor
from cat.mad_hatter.plugin import Plugin
import cat.utils as utils
from cat.utils import singleton


@singleton
class Tweedledum(MadHatter):
    """
    Tweedledum is the plugin manager of the Lizard. It is responsible for:
    - Installing a plugin
    - Uninstalling a plugin
    - Loading plugins
    - Prioritizing hooks
    - Executing hooks
    - Activating a plugin at a system level

    Notes:
    ------
    Tweedledum is the one that knows about the plugins, the hooks, the tools and the forms. It is the one that
    executes the hooks and the tools, and the one that loads the forms. It:
    - loads and execute plugins
    - enter into the plugin folder and loads everything that is decorated or named properly
    - orders plugged in hooks by name and priority
    - exposes functionality to the lizard and cats to execute hooks and tools
    """

    def __init__(self):
        self.__skip_folders = ["__pycache__", "lost+found"]
        self.__plugins_folder = utils.get_plugins_path()

        # this callback is set from outside to be notified when plugin install is completed
        self.on_finish_plugin_install_callback = lambda plugin_id: None
        # this callback is set from outside to be notified when plugin uninstall is completed
        self.on_finish_plugin_uninstall_callback = lambda plugin_id: None

        super().__init__()

    def install_plugin(self, package_plugin: str) -> str:
        # extract zip/tar file into plugin folder
        extractor = PluginExtractor(package_plugin)
        plugin_path = extractor.extract(self.__plugins_folder)
        plugin_id = extractor.id
        
        plugin_existed = self.plugin_exists(plugin_id)
        was_active = plugin_id in self.active_plugins if plugin_existed else False
        
        if plugin_existed:
            self.deactivate_plugin(plugin_id)
            del self.plugins[plugin_id]

        # create plugin obj, and eventually activate it
        if plugin_id != "core_plugin" and self.__load_plugin(plugin_path):
            if not plugin_existed or was_active:
                self.activate_plugin(plugin_id)

        # notify install has finished (the Lizard will ensure to notify the already loaded Cheshire Cats about the
        # plugin)
        self.on_finish_plugin_install_callback(plugin_id)

        return plugin_id

    def uninstall_plugin(self, plugin_id: str):
        if self.plugin_exists(plugin_id) and plugin_id != "core_plugin":
            # deactivate plugin if it is active (will sync cache)
            if plugin_id in self.active_plugins:
                self.deactivate_plugin(plugin_id)

            # remove plugin from cache
            plugin_path = self.plugins[plugin_id].path
            del self.plugins[plugin_id]

            # remove plugin folder
            shutil.rmtree(plugin_path)

        # notify uninstall has finished (the Lizard will ensure to completely remove the plugin from the system,
        # including DB)
        self.on_finish_plugin_uninstall_callback(plugin_id)

    # discover all plugins
    def find_plugins(self):
        # emptying plugin dictionary, plugins will be discovered from disk
        # and stored in a dictionary plugin_id -> plugin_obj
        self.plugins = {}

        # plugins are found in the plugins folder,
        # plus the default core plugin (where default hooks and tools are defined)
        core_plugin_folder = "cat/mad_hatter/core_plugin/"

        # plugin folder is "cat/plugins/" in production, "tests/mocks/mock_plugin_folder/" during tests
        all_plugin_folders = [core_plugin_folder] + glob.glob(
            f"{self.__plugins_folder}*/"
        )

        # discover plugins, folder by folder
        active_plugins = []
        for folder in all_plugin_folders:
            plugin_id = os.path.basename(os.path.normpath(folder))
            if plugin_id in self.__skip_folders:
                continue

            if not self.__load_plugin(folder):
                log.error(f"Plugin {plugin_id} could not be loaded")
                continue

            try:
                self.plugins[plugin_id].activate(self.agent_key)
                active_plugins.append(plugin_id)
            except Exception as e:
                # Couldn't activate the plugin -> Deactivate it
                self.deactivate_plugin(plugin_id)
                raise e

        crud_settings.upsert_setting_by_name(self.agent_key, Setting(name="active_plugins", value=active_plugins))
        self.active_plugins = self.load_active_plugins_from_db()

        log.info("ACTIVE PLUGINS:")
        log.info(self.active_plugins)

        self._sync_hooks_tools_and_forms()

    def __load_plugin(self, plugin_path: str) -> bool:
        # Instantiate plugin.
        #   If the plugin is inactive, only manifest will be loaded
        #   If active, also settings, tools and hooks
        try:
            plugin = Plugin(plugin_path)
            # if plugin is valid, keep a reference
            self.plugins[plugin.id] = plugin
            return True
        except Exception as e:
            # Something happened while loading the plugin.
            # Print the error and go on with the others.
            log.error(str(e))
            return False

    def on_plugin_activation(self, plugin_id: str):
        # Activate the plugin
        self.plugins[plugin_id].activate(self.agent_key)

    def on_plugin_deactivation(self, plugin_id: str):
        # Deactivate the plugin
        self.plugins[plugin_id].deactivate(self.agent_key)

    @property
    def agent_key(self):
        return DEFAULT_SYSTEM_KEY
