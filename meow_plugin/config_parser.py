import json
import pathlib
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mcdreforged.plugin.si.server_interface import PluginServerInterface

DEFAULT_CONFIG = {
    "config_version":1,
    "enable": True,
    "command_prefix": "!!meow",
    "msg_suffix":"",
    "random_sentence_files": [
      {
        "file_name": "meow.txt",
        "enable": True,
        "trigger_regex": "^(meow|miao|喵喵喵)",
        "priority": 0
      }
    ],
      "resources": [
        "lang",
        "data"
    ]
}

class MeowConfigParser(object):
    def __init__(self, server_interface: "PluginServerInterface"):

        self.server_interface = server_interface
        self._load_config_file()
        self._check_config_file_version()
        self.release_default_random_sentence_data()

        self.config_file:pathlib.Path

    def _load_config_file(self):
        self.config_file = pathlib.Path(self.server_interface.get_data_folder()) / "meow_config.json"
        if not self.config_file.exists():
            self.config: Dict = DEFAULT_CONFIG
            try:
                # with self.server_interface.open_bundled_file(relative_file_path="data/default_config.json") as file_handler:
                #     config_file.write_bytes(file_handler.read())

                self.config_file.write_text(json.dumps(DEFAULT_CONFIG, indent=4))

                self.server_interface.logger.info("Successfully created plugin configuration file.")
            except Exception as e:
                self.server_interface.logger.warning(f"Unable to create plugin configuration file: {e}")
        else:
            try:
                self.config = json.loads(self.config_file.read_text(encoding="utf-8"))
            except Exception as e:
                self.server_interface.logger.warning(f"Fail to read plugin configuration file: {e}")

    def _check_config_file_version(self):
        if DEFAULT_CONFIG.get("config_version", 0) > self.config.get("config_version", 0):
            merged_config = DEFAULT_CONFIG.copy()

            overlapping_keys = set(DEFAULT_CONFIG.keys()) & set(self.config.keys())
            overlapping_keys.discard("config_version")

            for key in overlapping_keys:
                merged_config[key] = self.config[key]

            self.config = merged_config
            self.config_file.write_text(json.dumps(merged_config, indent=4))

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
