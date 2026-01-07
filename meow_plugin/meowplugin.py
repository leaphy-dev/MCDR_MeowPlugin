import pathlib
import random
import re
import linecache
from typing import Dict, List

from mcdreforged import MCDRPluginEvents
from mcdreforged.handler.impl import BukkitHandler
from mcdreforged.api.types import *
from mcdreforged.info_reactor.info import Info as MCDR_info
from mcdreforged.api.command import  SimpleCommandBuilder

from meow_plugin.config_parser import MeowConfigParser


class MeowHandler(BukkitHandler):
    def __init__(self, server, config):
        self.server = server
        self.config = config
    def get_name(self) -> str:
        return "meow_handler"

    def handle_player_prefix(self, info: MCDR_info) -> (str, str):
        # 使用更灵活的正则表达式，[Not Secure] 前缀可选
        pattern = r'(?:\[Not Secure\]\s*)?<\[\w+](?P<name>[^>]+)> (?P<message>.*)'
        m = re.fullmatch(pattern, info.content)

        if m is not None and self._verify_player_name(m["name"]):
            info.player = m["name"]
            info.content = m["message"]
        return info

    @staticmethod
    def remove_command_msg_suffix(msg:str, suffix:str):
        if msg.startswith("!!"):
            return msg[0:len(msg)-len(suffix)]
        else:
            return msg

    def parse_server_stdout(self, text: str):
        info: MCDR_info = super().parse_server_stdout(text)
        if not info.player:
            info = self.handle_player_prefix(info) # dataclass可哈希

        if info.is_player:
            info.content = self.remove_command_msg_suffix(info.content, self.config.get("msg_suffix", ""))

        return info


class MeowPlugin(object):
    def __init__(self,server:PluginServerInterface):
        self.server = server
        self.config_parser = MeowConfigParser(self.server)
        self.config: Dict = self.config_parser.config

        self.handler = MeowHandler(server = self.server, config=self.config)
        self.server.register_server_handler(self.handler)

        self.command_prefix = self.config.get("command_prefix", "!!meow")
        self.command_builder = SimpleCommandBuilder()
        self.register_commands()
        self.command_builder.register(self.server)

        self.random_meow_sentence_data: List[Dict] = []
        self._init_random_sentence()
        self.server.register_event_listener(MCDRPluginEvents.USER_INFO,callback=self.random_meow_sentence)

    def __str__(self):
        return  self.server.get_self_metadata().name + "@" +str(self.server.get_self_metadata().version)

    def _init_random_sentence(self):
        self.random_meow_sentence_data = []
        for f in self.config.get("random_sentence_files", tuple()):
            if f.get("file_name", "") and f.get("enable") and f.get("trigger_regex"):
                try:
                    f["compiled_regex"] = re.compile(f.get("trigger_regex", ""))

                    file_path = pathlib.Path(self.server.get_data_folder()) / f.get("file_name")
                    with open(file_path, 'r', encoding='utf-8') as fp:
                        f["lines"] = sum(1 for _ in fp)

                    self.random_meow_sentence_data.append(f)
                    self.random_meow_sentence_data.sort(key=lambda i: i.get("priority", 100))
                except re.error as e:
                    self.server.logger.warning(f"Invalid regex: {e}")

    # @event_listener(MCDRPluginEvents.USER_INFO)
    def random_meow_sentence(self, _, msg: Info) -> None:
        content = msg.content

        for i in self.random_meow_sentence_data:
            if "compiled_regex" in i and i["compiled_regex"].search(content):
                file = pathlib.Path(self.server.get_data_folder()) / i.get("file_name")
                random_line = linecache.getline(str(file), random.randint(1, i.get("lines")))
                self.server.say(random_line.strip())
                return

    def meow_command(self,command:str):
        _flag = False
        command = command.strip()
        if not command.startswith(self.command_prefix):
            command = self.command_prefix + " " + command
        def decorator(func):
            nonlocal _flag
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            if not _flag:
                self.command_builder.command(command, func)
                _flag = True
            return wrapper
        return decorator

    def register_commands(self):

        @self.meow_command(command="!!meow about")
        def about_command(source: CommandSource):
            source.reply(str(self))
