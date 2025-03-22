import asyncio
import yaml


from utils.decorators import *
from utils.plugin import PluginBase
from bs4 import BeautifulSoup
from wcferry import Wcf, WxMsg
from loguru import logger
from utils.LegendBot import LegendWechatBot
import re

class AcceptFriend(PluginBase):

    # changelog
    # 1.0.0 2025/3/7 初始版本

    def __init__(self):
        super().__init__()

        pluginConfig = yaml.safe_load(open('plugins/AcceptFriend/config.yaml', 'r', encoding='utf-8').read())

        self.config = pluginConfig['AcceptFriend']
        self.enable = self.config['enable']
    
    @on_other_message
    async def handleRequest(self, bot: LegendWechatBot, msg: WxMsg):
        # 如果功能未启用或消息类型不是37，则返回
        if not self.enable or msg.type != 37:
            return

        # 使用BeautifulSoup解析消息内容
        bs = BeautifulSoup(msg.content, 'lxml-xml')
        # 查找消息元素
        msg_ = bs.find('msg')
        # 如果找到了消息元素
        if msg_:
            # 获取场景值
            scene = int(msg_.get('scene'))
            # 获取加密用户名
            v3 = msg_.get('encryptusername')
            # 获取票据
            v4 = msg_.get('ticket')
            # 获取用户名
            userName = msg_.get('fromusername')
            # 如果接受新好友请求成功
            if bot.accept_new_friend(v3, v4, scene):
                # 记录成功信息
                logger.success(f'已接受好友请求: {userName}')
                return
            else:
                # 记录失败信息
                logger.warning(f'接受好友请求失败: {userName}')
                return
        else:
            # 如果没有找到消息元素，则返回
            return
    
    @on_system_message
    async def handleNewFriend(self, bot: LegendWechatBot, msg: WxMsg):
        # 使用正则表达式匹配消息内容，获取新朋友的昵称
        nickName = re.findall(r"你已添加了(.*)，现在可以开始聊天了。", msg.content)
        # 如果匹配成功，则将新朋友的昵称赋值给nickName变量
        if nickName:
            nickName = nickName[0]
        # 如果新朋友的昵称存在，且启用了新朋友处理功能，且消息类型为10000或10002，则发送欢迎消息
        if nickName and self.enable :
            bot.sendMsg(f'你好呀, {nickName}', msg.sender, None)
            return