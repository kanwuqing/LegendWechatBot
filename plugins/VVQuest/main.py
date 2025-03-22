import hashlib

import asyncio
import yaml
from database.LegendBotDB import *
import shutil

from utils.decorators import *
from utils.plugin import PluginBase
from bs4 import BeautifulSoup
from wcferry import Wcf, WxMsg
from loguru import logger
from utils.LegendBot import LegendWechatBot
import re
import os
import threading

class VVQuest(PluginBase):

    # changelog
    # 1.0.0 2025/3/7 初始版本

    def __init__(self):
        super().__init__()

        pluginConfig = yaml.safe_load(open('plugins/VVQuest/config.yaml', 'r', encoding='utf-8').read())

        self.config = pluginConfig['VVQuest']
        self.enable = self.config['enable']
        
        if self.enable:
            from .services.image_search import ImageSearch
            
            self.im = ImageSearch('local')
            
            if not os.path.exists(self.im._get_cache_file()):
                logger.info('未找到缓存, 正在生成')
                self.im.generate_cache()
        
    @on_text_message
    async def VVQuest(self, bot: LegendWechatBot, msg: WxMsg):
        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.sender, None
        
        if not self.enable:
            return
            
        if msg.content == 'vv':
            bot.sendMsg(f'智能检索张维为表情包, 项目连接:https://github.com/DanielZhangyc/VVQuest\n使用方法: vv [关键词]\n注意事项: 请不要频繁请求', to, at)
            return
        if msg.content.startswith('vv '):
            query = msg.content[3:]
            if query == '':
                return

            LegendBotDB().set_running(msg.sender, True)
            # task = threading.Thread(target=self.getRes, args=(bot, msg, to, at))
            # task.start()
            # task.join()
            query = msg.content[3:]
            if query == '':
                return

            res = await run_sync(self.im.search)(query, 1)

            if len(res) == 0:
                bot.sendMsg('未找到相关表情包', to, at)
                return
            
            original_file = res[0].replace('\\', '/')
            file_extension = os.path.splitext(original_file)[1]
            hash_object = hashlib.md5(original_file.encode())
            hashed_filename = hash_object.hexdigest() + file_extension
            temp_dir = 'plugins/VVQuest/cache'
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            temp_file_path = os.path.join(temp_dir, hashed_filename)
            shutil.copyfile(original_file, temp_file_path)

            # 获取绝对路径
            abs_temp_file_path = os.path.abspath(temp_file_path)

            # 发送文件
            bot.send_image(abs_temp_file_path, to)

            # 删除临时文件
            os.remove(abs_temp_file_path)

            LegendBotDB().set_running(msg.sender, False)

            
    '''
    def getRes(self, bot: LegendWechatBot, msg: WxMsg, to, at):
        import time
        time.sleep(5)
        query = msg.content[3:]
        if query == '':
            return

        res = self.im.search(query, 1)

        if len(res) == 0:
            bot.sendMsg('未找到相关表情包', to, at)
            return
        
        original_file = res[0].replace('\\', '/')
        file_extension = os.path.splitext(original_file)[1]
        hash_object = hashlib.md5(original_file.encode())
        hashed_filename = hash_object.hexdigest() + file_extension
        temp_dir = 'plugins/VVQuest/cache'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        temp_file_path = os.path.join(temp_dir, hashed_filename)
        shutil.copyfile(original_file, temp_file_path)

        # 获取绝对路径
        abs_temp_file_path = os.path.abspath(temp_file_path)

        # 发送文件
        bot.send_image(abs_temp_file_path, to)

        # 删除临时文件
        os.remove(abs_temp_file_path)

        LegendBotDB().set_running(msg.sender, False)
        '''