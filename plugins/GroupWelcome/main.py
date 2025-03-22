import yaml
import xml.etree.ElementTree as ET
from datetime import datetime

from loguru import logger

from wcferry import Wcf, WxMsg
from utils.LegendBot import LegendWechatBot
from utils.decorators import on_system_message
from utils.plugin import PluginBase
import re
from utils.dictTools import *
import time
from database.LegendBotDB import *

class GroupWelcome(PluginBase):

    def __init__(self):
        super().__init__()

        with open("plugins/GroupWelcome/config.yaml", "rb") as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config["GroupWelcome"]

        self.enable = config["enable"]
        self.welcome_message = config["welcome-message"]
        self.url = config["url"]

    @on_system_message
    async def groupWelcome(self, bot: LegendWechatBot, message: WxMsg):
        if not self.enable:
            return

        # 如果不是群聊消息，则返回
        if not message.from_group():
            return

        # 如果消息类型不是10000或10002，则返回
        if message.type != 10000 and message.type != 10002:
            return

        # 如果群聊不在白名单中，则返回
        if not LegendBotDB().get_chatroom_whitelist(message.roomid):
            return

        # 如果消息内容中包含邀请加入群聊的信息，则解析成员信息
        if re.findall(r'"(.*?)"邀请"(.*?)"加入了群聊', message.content):  # 通过邀请加入群聊
            new_members = self._parse_member_info(bot, message, "invitation")
        elif re.findall(r'"(.*)"加入了群聊', message.content):  # 直接加入群聊
            new_members = self._parse_member_info(bot, message, "direct")
        elif re.findall(r'"(.*?)"通过(.*?)加入群聊', message.content):  # 通过邀请链接加入群聊
            new_members = self._parse_member_info(bot, message, "inviters")
        else:
            logger.warning(f"未知的入群方式: ")
            return

        if not new_members:
            return

        for member in new_members:
            wxid = member["wxid"]
            nickname = member["nickname"]

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            img = bot.query_sql('MicroMsg.db', f'SELECT bigHeadImgUrl FROM ContactHeadImgUrl WHERE usrName="{wxid}";')
            if img:
                img = img[0]['bigHeadImgUrl']
            else:
                img = ''
            logger.debug(f"{nickname} {str(wxid)} {img} 加入了群聊")
            bot.send_rich_text(nickname, str(wxid), f"👏欢迎 {nickname} 加入群聊!🎉", f"⌚时间：{now}\n{self.welcome_message}\n🔗点击查看更多信息", 'https://kanwuqing.github.io', img, message.roomid)
        return

    @staticmethod
    def _parse_member_info(bot: Wcf, message: WxMsg, link: str):
        # 定义一个空列表，用于存储用户信息
        user = []
        # 直接加群
        if link == "direct":
            pattern = r'"(.*)"加入了群聊'
            user = re.findall(pattern, message.content)[0].split("、")
        
        # 匿名邀请加群
        elif link == "inviters":
            pattern = r'"(.*?)"通过(.*?)加入群聊'
            user = re.findall(pattern, message.content)[0][0].split("、")

        # 邀请加群
        elif link == "invitation":
            pattern = r'"(.*?)"邀请"(.*?)"加入了群聊'
            user = re.findall(pattern, message.content)[0][1].split("、")
        
        # 定义一个空列表，用于存储用户信息
        users = []
        # 暂停3秒
        time.sleep(3)
        # 获取群聊成员信息
        mem = bot.get_chatroom_members(message.roomid)
        # 打印群聊成员信息
        logger.debug(mem)
        # 遍历用户信息
        for i in user:
            # 将用户信息添加到users列表中
            users.append({"wxid": get_key(mem, i), "nickname": i})
        # 返回用户信息
        return users