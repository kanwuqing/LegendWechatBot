import yaml

from loguru import logger
import os
import shutil
from wcferry import Wcf, WxMsg
from utils.LegendBot import LegendWechatBot
from utils.decorators import on_text_message, schedule, on_quote_message, run_sync
from utils.plugin import PluginBase
import re
from utils.dictTools import *
import time
from database.LegendBotDB import *
from database.messageDB import MessageDB
from bs4 import BeautifulSoup
import traceback
import re

class ImageDeal(PluginBase):

    def __init__(self):
        super().__init__()

        with open("plugins/ImageDeal/config.yaml", "rb") as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config["ImageDeal"]

        self.enable = config["enable"]
        self.folder = config["folder"]
        self.autoDel = config["autoDel"]

        self.folder = os.path.join(os.path.dirname(__file__), self.folder)
        # logger.debug(self.folder)
        
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
    
    @on_text_message
    async def dealImage(self, bot: LegendWechatBot, msg: WxMsg):
        if not self.enable:
            return
        
        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.sender, None
        
        if msg.content == '多媒体':
            bot.sendMsg('多媒体相关功能, 详细请发送具体命令前缀查看`下载多媒体` 下载多媒体\n`删除多媒体 多媒体名.后缀名` 删除多媒体\n`重命名多媒体 多媒体名.后缀名 新多媒体名.后缀名` 重命名多媒体\n`已有多媒体` 查看已有多媒体', to, at)
        

        #* 下载多媒体
        if msg.content == '下载多媒体':
            bot.sendMsg('下载多媒体, 用于制作表情包等插件功能\n命令格式: `下载多媒体`, 并引用需要下载的多媒体(必须是自己发的, 引用他人发的无效, 引用文件无效)\n每个人最多同时存在5张多媒体, 总大小不超过20MB', to, at)
            return

        #* 已有多媒体
        if msg.content == '已有多媒体':
            res = '已有多媒体: 多媒体名 多媒体大小\n'
            #遍历文件夹, 获取多媒体名称与大小
            if os.path.exists(os.path.join(self.folder, msg.sender)):
                for root, _, files in os.walk(os.path.join(self.folder, msg.sender)):
                    for file in files:
                        res += f"{file} {os.path.getsize(os.path.join(root, file)) / 1024:.2f}KB\n"
            bot.sendMsg(res, to, at)
            
        
        #* 删除多媒体
        if msg.content == '删除多媒体':
            bot.sendMsg('删除多媒体, 命令格式: `删除多媒体 多媒体名.后缀名(在下载成功后返回)`', to, at)
            return
        if msg.content.startswith('删除多媒体 '):
            msg.content = msg.content.replace('删除多媒体 ', '')
            if not os.path.exists(os.path.join(self.folder, msg.sender, msg.content)):
                bot.sendMsg('多媒体不存在', to, at)
                return

            os.remove(os.path.join(self.folder, msg.sender, msg.content))
            bot.sendMsg('删除成功', to, at)
            return

        #* 重命名多媒体
        if msg.content == '重命名多媒体':
            bot.sendMsg('重命名多媒体, 命令格式: `重命名多媒体 多媒体名.后缀名(在下载成功后返回) 新多媒体名.后缀名(命名限制为windows限制, 另外不能有空格)`', to, at)
            return
        if msg.content.startswith('重命名多媒体 '):
            msg.content = msg.content[7: ]
            if not os.path.exists(os.path.join(self.folder, msg.sender, msg.content.split(' ')[0])):
                bot.sendMsg('多媒体不存在', to, at)
                return

            if len(msg.content.split(' ')) != 2:
                bot.sendMsg('命令格式错误', to, at)
                return

            if not os.path.exists(os.path.join(self.folder, msg.sender)):
                os.mkdir(os.path.join(self.folder, msg.sender))
            
            
            if os.path.exists(os.path.join(self.folder, msg.sender, msg.content.split(' ')[1])):
                bot.sendMsg('新多媒体名已存在', to, at)
                return
            
            filename = msg.content.split(' ')[1]
            if self.is_valid_filename(filename) and (filename.endswith('.jpg') or filename.endswith('.png')):
                os.rename(os.path.join(self.folder, msg.sender, msg.content.split(' ')[0]), os.path.join(self.folder, msg.sender, msg.content.split(' ')[1]))
                bot.sendMsg('重命名成功', to, at)
                return
            else:
                bot.sendMsg('新多媒体名包含非法字符', to, at)
                return
    
    def is_valid_filename(self, filename) -> bool:
    # 检查文件名是否包含非法字符
        if re.search(r'[<>:"/\\|?*]', filename):
            return False

        # 检查文件名是否以空格或句点结尾
        if filename.endswith(' ') or filename.endswith('.'):
            return False

        # 检查文件名是否为保留名称
        reserved_names = [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        ]
        if filename.upper() in reserved_names:
            return False

        return True

    @on_quote_message
    async def downloadMedia(self, bot: LegendWechatBot, msg: WxMsg):
        try:
            if not self.enable:
                return
            
            if msg.from_group():
                to, at = msg.roomid, msg.sender
            else:
                to, at = msg.sender, None

            bs = BeautifulSoup(msg.content, 'lxml-xml')

            msg.content = bs.find('title').text
            quote = bs.find('refermsg')

            if msg.content == '下载多媒体':
                if quote is None:
                    bot.sendMsg('引用无效, 请重新引用需要下载的多媒体', to, at)
                    return
                if quote.find('type').text != '3' and quote.find('type').text != '43':
                    bot.sendMsg('引用无效, 请重新引用需要下载的多媒体', to, at)
                    return
                if quote.find('chatusr').text != msg.sender:
                    bot.sendMsg('引用无效, 这不是你发的', to, at)
                    return
                
                if not os.path.exists(os.path.join(self.folder, msg.sender)):
                    os.mkdir(os.path.join(self.folder, msg.sender))

                if len(os.listdir(os.path.join(self.folder, msg.sender))) > 10 or self.calcSize(msg.sender) > 20:
                    bot.sendMsg('多媒体数量或大小超过限制, 请删除一些多媒体', to, at)
                    return
                
                msgId = int(quote.find('svrid').text)

                logger.debug(f"msgId: {msgId}")

                quoteMsg = await MessageDB().get_messages(msg_id=msgId)

                if not quoteMsg:
                    bot.sendMsg('引用无效, 请重新引用需要下载的多媒体', to, at)
                    return
                
                res = None
                
                if quoteMsg[0].type == 3:
                    res = await run_sync(bot.download_image)(msgId, quoteMsg[0].extra, os.path.abspath(os.path.join(self.folder, msg.sender)), 30)
                
                elif quoteMsg[0].type == 43:
                    res = await run_sync(bot.download_video)(msgId, quoteMsg[0].thumb, os.path.abspath(os.path.join(self.folder, msg.sender)), 30)

                if not res:
                    bot.sendMsg('多媒体下载失败', to, at)
                    logger.warning(f"多媒体下载失败, msgId: {msgId}")
                else:
                    bot.sendMsg(f'多媒体下载完成, 保存为{os.path.basename(res)}', to, at)
        except Exception as e:
            logger.error(f"多媒体下载失败, msgId: {msgId}, error: {e}, traceback: {traceback.format_exc()}")
            bot.sendMsg('多媒体下载失败', to, at)
            return

    def calcSize(self, wxid):
        # 计算文件夹总大小
        size = 0
        for root, _, files in os.walk(os.path.join(self.folder, wxid)):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size / 1024 / 1024
    
    @schedule('interval', days=1)
    async def _del(self, *args, **kwargs):
        if self.autoDel:
            try:
                shutil.rmtree(self.folder)
                os.mkdir(self.folder)
            except:
                logger.error("删除文件夹失败")