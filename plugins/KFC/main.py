import yaml
import xml.etree.ElementTree as ET
from datetime import datetime
import difflib
from loguru import logger

from wcferry import WxMsg

import os
import shutil
from utils.decorators import on_text_message, schedule
from utils.plugin import PluginBase
from utils.LegendBot import LegendWechatBot
from utils.dictTools import *
from database.LegendBotDB import LegendBotDB
import traceback
import aiohttp
import json


class KFC(PluginBase):

    def __init__(self):
        super().__init__()
        with open("plugins/KFC/config.yaml", "rb") as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config["KFC"]
        self.enable = config["enable"]

    
    @on_text_message
    async def kfc(self, bot: LegendWechatBot, msg: WxMsg):
        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.sender, None
        
        if not self.enable:
            return
        
        if msg.content == 'kfc':
            try:
                LegendBotDB().set_running(msg.sender, True)
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.pearktrue.cn/api/kfc?type=json"
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            logger.warning(f"天气查询失败: {resp.status}")
                            return
                        rsp1 = await resp.json()
                bot.sendMsg(rsp1['text'].replace('\\n', '\n'), to, at)
                LegendBotDB().set_running(msg.sender, False)
            except Exception as e:
                logger.error(f"KFC查询失败: {e}")
                LegendBotDB().set_running(msg.sender, False)
                bot.sendMsg("KFC查询失败", to, at)
    
    @schedule('cron', day_of_week='thu', hour=17, minute=0, second=0, misfire_grace_time=None)
    async def send_kfc(self, bot: LegendWechatBot):
        if not self.enable:
            return

        for group in LegendBotDB().get_chatroom_list():
            async with aiohttp.ClientSession() as session:
                url = f"https://api.pearktrue.cn/api/kfc?type=json"
                async with session.get(url) as resp:
                    if resp.status != 200:
                            logger.warning(f"KFC调用失败: {resp.status}")
                            return
                    rsp1 = await resp.json()
            bot.sendMsg(rsp1['text'], group)