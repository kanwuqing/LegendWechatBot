import yaml
import xml.etree.ElementTree as ET
from datetime import datetime
import difflib
from loguru import logger

from wcferry import WxMsg

import os
import sys
import importlib
from utils.decorators import on_text_message
from utils.plugin import PluginBase
from utils.LegendBot import LegendWechatBot
from utils.dictTools import *
from database.LegendBotDB import LegendBotDB
import traceback


class Meme(PluginBase):

    def __init__(self):
        super().__init__()

        with open("plugins/Meme/config.yaml", "rb") as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config["Meme"]
        self.enable = config["enable"]

        if self.enable:
            pth = os.path.join(os.path.dirname(__file__), 'temp')
            if not os.path.exists(pth):
                os.mkdir(pth)
            os1 = os.getcwd()
            sys1 = sys.path
            os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))

            meme_processor = importlib.import_module("meme_processor")
            self.handle_message = meme_processor.handle_message

            os.chdir(os1)
            sys.path = sys1
    
    @on_text_message
    async def meme(self, bot: LegendWechatBot, msg: WxMsg):
        # 判断消息是否来自群聊
        if msg.from_group():
            # 如果是群聊，则将消息发送者和群聊ID赋值给to和at
            to, at = msg.roomid, msg.sender
        else:
            # 如果不是群聊，则将消息发送者赋值给to，at为None
            to, at = msg.sender, None
        
        # 如果功能未启用，则直接返回
        if not self.enable:
            return
        
        if msg.content.startswith("meme"):
            try:
                await self.handle_message(bot, msg, to, at)
            except Exception as e:
                logger.error(f"处理消息时发生错误: {e}")
                logger.error(traceback.format_exc())
                return