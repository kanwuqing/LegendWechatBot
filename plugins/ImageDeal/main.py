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
        
        if msg.content == '图片':
            bot.sendMsg('图片相关功能, 详细请发送具体命令前缀查看`下载图片` 下载图片\n`删除图片 图片名.后缀名` 删除图片\n`重命名图片 图片名.后缀名 新图片名.后缀名` 重命名图片', to, at)

        #* 下载图片
        if msg.content == '下载图片':
            bot.sendMsg('下载图片, 用于制作表情包等插件功能\n命令格式: `下载图片`, 并引用需要下载的图片(必须是自己发的, 引用他人发的无效, 引用文件无效)\n每个人最多同时存在5张图片, 总大小不超过20MB', to, at)
            return
        
        #* 删除图片
        if msg.content == '删除图片':
            bot.sendMsg('删除图片, 命令格式: `删除图片 图片名.后缀名(在下载成功后返回)`', to, at)
            return
        if msg.content.startswith('删除图片 '):
            msg.content = msg.content.replace('删除图片 ', '')
            if not os.path.exists(os.path.join(self.folder, msg.sender, msg.content)):
                bot.sendMsg('图片不存在', to, at)
                return

            os.remove(os.path.join(self.folder, msg.sender, msg.content))
            bot.sendMsg('删除成功', to, at)
            return

        #* 重命名图片
        if msg.content == '重命名图片':
            bot.sendMsg('重命名图片, 命令格式: `重命名图片 图片名.后缀名(在下载成功后返回) 新图片名.后缀名(命名限制为windows限制, 另外不能有空格)`', to, at)
            return
        if msg.content.startswith('重命名图片 '):
            msg.content = msg.content[6: ]
            if not os.path.exists(os.path.join(self.folder, msg.sender, msg.content.split(' ')[0])):
                bot.sendMsg('图片不存在', to, at)
                return

            if len(msg.content.split(' ')) != 2:
                bot.sendMsg('命令格式错误', to, at)
                return

            if not os.path.exists(os.path.join(self.folder, msg.sender)):
                os.mkdir(os.path.join(self.folder, msg.sender))
            
            
            if os.path.exists(os.path.join(self.folder, msg.sender, msg.content.split(' ')[1])):
                bot.sendMsg('新图片名已存在', to, at)
                return
            
            filename = msg.content.split(' ')[1]
            if self.is_valid_filename(filename) and (filename.endswith('.jpg') or filename.endswith('.png')):
                os.rename(os.path.join(self.folder, msg.sender, msg.content.split(' ')[0]), os.path.join(self.folder, msg.sender, msg.content.split(' ')[1]))
                bot.sendMsg('重命名成功', to, at)
                return
            else:
                bot.sendMsg('新图片名包含非法字符', to, at)
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
    async def downloadImage(self, bot: LegendWechatBot, msg: WxMsg):
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

            if msg.content == '下载图片':
                if quote is None:
                    bot.sendMsg('引用无效, 请重新引用需要下载的图片', to, at)
                    return
                if quote.find('type').text != '3':
                    bot.sendMsg('引用无效, 请重新引用需要下载的图片', to, at)
                    return
                if quote.find('chatusr').text != msg.sender:
                    bot.sendMsg('引用无效, 这不是你发的', to, at)
                    return
                
                if not os.path.exists(os.path.join(self.folder, msg.sender)):
                    os.mkdir(os.path.join(self.folder, msg.sender))

                if len(os.listdir(os.path.join(self.folder, msg.sender))) > 5 or self.calcSize(msg.sender) > 20:
                    bot.sendMsg('图片数量或大小超过限制, 请删除一些图片', to, at)
                    return
                
                msgId = int(quote.find('svrid').text)

                logger.debug(f"msgId: {msgId}")

                quoteMsg = await MessageDB().get_messages(msg_id=msgId)

                if not quoteMsg:
                    bot.sendMsg('引用无效, 请重新引用需要下载的图片', to, at)
                    return

                res = await run_sync(bot.download_image)(msgId, quoteMsg[0].extra, os.path.abspath(os.path.join(self.folder, msg.sender)), 10)

                if not res:
                    bot.sendMsg('图片下载失败', to, at)
                    logger.warning(f"图片下载失败, msgId: {msgId}")
                else:
                    bot.sendMsg(f'图片下载完成, 保存为{os.path.basename(res)}', to, at)
        except Exception as e:
            logger.error(f"图片下载失败, msgId: {msgId}, error: {e}, traceback: {traceback.format_exc()}")
            bot.sendMsg('图片下载失败', to, at)
            return

    def calcSize(self, wxid):
        # 计算文件夹总大小
        size = 0
        for root, _, files in os.walk(os.path.join(self.folder, wxid)):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size / 1024 / 1024
    
    @schedule('interval', days=1)
    async def _del(self):
        if self.autoDel:
            try:
                shutil.rmtree(self.folder)
                os.mkdir(self.folder)
            except:
                logger.error("删除文件夹失败")