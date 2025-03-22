import yaml

from loguru import logger
import os
import shutil
from wcferry import Wcf, WxMsg
from utils.LegendBot import LegendWechatBot
from utils.decorators import on_text_message, schedule, on_quote_message
from utils.plugin import PluginBase
import re
from utils.dictTools import *
import time
from database.LegendBotDB import *
import re

class Menu(PluginBase):

    def __init__(self):
        super().__init__()

        with open("plugins/Menu/config.yaml", "rb") as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config["Menu"]
        self.enable = config["enable"]

        self.load_folders()
    
    def load_folders(self):
        self.info = {}
        folders = os.listdir(os.path.join(os.path.abspath(__file__), '../..'))
        folders.remove('Menu')

        for folder in folders:
            with open(os.path.join(os.getcwd(), 'plugins', folder, 'config.yaml'), "rb") as f:
                plugin_config = yaml.safe_load(f)
            name = list(plugin_config.keys())[0]
            plugin_config = plugin_config[name]

            if 'description' not in list(plugin_config.keys()) or not plugin_config['enable'] or 'cmd' not in list(plugin_config.keys()):
                logger.debug(folder)
                continue

            self.info[folder] = {
                'name': name,
                'cmd': plugin_config['cmd'],
                'description': plugin_config["description"],
            }
        logger.debug(self.info)

    
    @on_text_message
    async def menu(self, bot: LegendWechatBot, msg: WxMsg):
        if not self.enable:
            return
        
        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.sender, None
        
        if msg.content == '菜单':
            text = '名称\t命令\t描述\n'
            for info in self.info:
                text += f'{info}\t{self.info[info]["cmd"]}\t{self.info[info]["description"]}\n'
            bot.sendMsg(text, to, at)
            return