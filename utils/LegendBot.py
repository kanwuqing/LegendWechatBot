from config.config import config
from database import *
from typing import Dict, Any
from .asyncEnsure import sem, LegendSemaphore
from loguru import logger
from .eventManager import EventManager
from database.LegendBotDB import LegendBotDB
from database.messageDB import MessageDB
from wcferry import Wcf, WxMsg
from utils.dfa import dfa
from bs4 import BeautifulSoup
import traceback
import time
import random
from .changeHandler import restartProgram

class LegendWechatBot(Wcf):
    def __init__(self, host: str = None, port: int = 10086, debug: bool = True, block: bool = True) -> None:
        super().__init__(host, port, debug, block)
    
    def sendMsg(self, msg: str, receiver: str, at_list: list | str = None) -> None:
        """ 发送消息
        :param msg: 消息字符串
        :param receiver: 接收人wxid或者群id
        :param at_list: 要@的wxid, @所有人的wxid为：notify@all
        """
        # msg 中需要有 @ 名单中一样数量的 @
        time.sleep(random.randint(1, 5) / random.randint(1, 10))
        ats = ""
        at = ""
        if isinstance(at_list, str):
            at_list = [at_list]
        if at_list:
            if at_list == ["notify@all"]:  # @所有人
                ats = "@所有人"
            else:
                for wxid in at_list:
                    # 根据 wxid 查找群昵称
                    ats += f"@{self.get_alias_in_chatroom(wxid, receiver)}\u2005"
                    at += f"{wxid},"
        at = at[:-1] if at.endswith(',') else at
        # {msg}{ats} 表示要发送的消息内容后面紧跟@，例如 北京天气情况为：xxx @张三
        if ats == "":
            self.send_text(msg, receiver, at)
        else:
            self.send_text(f"{ats} {msg}", receiver, at)


class LegendBot:
    def __init__(self, bot: LegendWechatBot):
        self.bot = bot
        self.wxid = bot.self_wxid
        self.DB = LegendBotDB()
        self.msgDB = MessageDB()
    
    async def process_message(self, msg: WxMsg):
        """处理接收到的消息"""
        try:
            if msg.from_group():
                to, at = msg.roomid, msg.sender
                msg.content = msg.content.replace(f"@to be legend ", "")
            else:
                to, at = msg.sender, None

            logger.debug("处理消息: {} - {}\n------------------------\n{}", msg.type, msg.content, msg.xml)

                
            async with sem['processMsg']:

                if msg.type == 10000 or msg.type == 10002:  # 系统消息
                    logger.debug(f'收到系统消息')
                    await EventManager.emit("system_message", self.bot, msg)
                if msg.type == 37:  # 好友请求
                    logger.debug(f'收到好友请求')
                    await EventManager.emit("other_message", self.bot, msg)
                if msg.type == 1:  # 文本消息
                    await self.msgDB.save_message(msg, self.bot.self_wxid)

                    if msg.content == '重启程序' and msg.sender in config.admin:
                        restartProgram()

                    if dfa.exists(msg.content):
                        self.DB.add_black(msg.sender, 2)
                        self.bot.sendMsg(f'说话太刑了, 黑名单指数+2, 请注意\n{dfa.filter_all(msg.content)}', to, at)
                        return
                
                    if ((msg.from_group() and msg.is_at(self.bot.self_wxid)) or not msg.from_group()) and self.DB.get_black(msg.sender) <= config.RobotConfig['black']:
                        if self.DB.get_running(msg.sender):
                            self.DB.add_black(msg.sender, 1)
                            self.bot.sendMsg('你还有正在运行的任务未完成, 黑名单指数+1, 请注意', to, at)
                            return
                        
                        logger.debug(f'收到文本消息')
                        await EventManager.emit("text_message", self.bot, msg)

                if msg.type == 3:  # 图片消息
                    logger.debug(f'收到图片消息')
                    await self.msgDB.save_message(msg, self.bot.self_wxid)

                    await EventManager.emit("image_message", self.bot, msg)
                
                if msg.type == 49:
                    logger.debug(f'收到引用消息')
                    await self.msgDB.save_message(msg, self.bot.self_wxid)
                    bs = BeautifulSoup(msg.content, 'lxml-xml')
                    content = bs.find('title').text

                    if dfa.exists(content):
                        self.DB.add_black(msg.sender, 2)
                        self.bot.sendMsg(f'说话太刑了, 黑名单指数+2, 请注意\n{dfa.filter_all(msg.content)}', to, at)
                        return
                
                    if ((msg.from_group() and msg.is_at(self.bot.self_wxid)) or not msg.from_group()) and self.DB.get_black(msg.sender) <= config.RobotConfig['black']:
                        if self.DB.get_running(msg.sender):
                            self.DB.add_black(msg.sender, 1)
                            self.bot.sendMsg('你还有正在运行的任务未完成, 黑名单指数+1, 请注意', to, at)
                            return
                    
                    await EventManager.emit("quote_message", self.bot, msg)

        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}")
            logger.error(traceback.format_exc())