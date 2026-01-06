import json
import pathlib
from typing import Dict

from mcdreforged.plugin.si.server_interface import PluginServerInterface


class MeowConfigParser(object):
    def __init__(self, server_interface: PluginServerInterface):

        self.server_interface = server_interface
        self._load_config_file()
        self.release_default_random_sentence_data()

    def _load_config_file(self):
        config_file = pathlib.Path(self.server_interface.get_data_folder()) / "meow_config.json"
        if not config_file.exists():
            try:
                with self.server_interface.open_bundled_file(relative_file_path="data/default_config.json") as file_handler:
                    config_file.write_bytes(file_handler.read())
                self.server_interface.logger.info("Successfully created plugin configuration file.")
            except Exception as e:
                self.server_interface.logger.warning(f"Unable to create plugin configuration file: {e}")

        self.config: Dict = json.loads(config_file.read_text(encoding="utf-8"))

    def reload_config(self):
        try:
            self._load_config_file()
            self.server_interface.logger.info("Successfully reloaded plugin configuration file.")
        except Exception as e:
            self.server_interface.logger.warning(f"Fail to reload plugin configuration file: {e}")

    def release_default_random_sentence_data(self):
        config_file = pathlib.Path(self.server_interface.get_data_folder()) / "meow.txt"
        if not config_file.exists():
            with self.server_interface.open_bundled_file(relative_file_path="data/meow.txt") as file_handler:
                config_file.write_bytes(file_handler.read())
