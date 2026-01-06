from mcdreforged import PluginServerInterface

from plugin.meowplugin import MeowPlugin


def on_load(server:PluginServerInterface, prev_module):
    plugin = MeowPlugin(server)
    server.logger.info('Meow Plugin loaded!')