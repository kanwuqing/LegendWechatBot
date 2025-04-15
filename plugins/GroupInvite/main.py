from utils.plugin import PluginBase
from utils.LegendBot import LegendWechatBot, WxMsg
from utils.decorators import on_text_message
from database.LegendBotDB import LegendBotDB
from loguru import logger
import traceback
import yaml
import random

class GroupInvite(PluginBase):
    def __init__(self):
        super().__init__()
        with open('plugins/GroupInvite/config.yaml', 'r', encoding='utf-8') as f:
            plugin_config = yaml.safe_load(f)

        self.config = plugin_config['GroupInvite']
        self.enable = self.config['enable']

    @on_text_message
    async def send_group_invite(self, bot: LegendWechatBot, msg: WxMsg):
        if not self.enable:
            return
        
        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.roomid, None

        try:
            # 检查是否为私聊消息
            if msg.content == '进群':
                bot.sendMsg('自动拉群功能: 发送`进群 Legend`进入随机交流群\n发送`进群 群聊列表`查看所有群聊\n发送`进群 群聊序号`获取指定群聊的邀请链接\n仅能在私聊中使用', to, at)

            if msg.from_group():
                return

            # 检查消息内容是否为邀请指令
            if msg.content.startswith("进群 "):
                sub = msg.content.split(" ")[1]  # 提取群聊 ID

                chatroom_list = LegendBotDB().get_chatrooms()

                logger.debug(chatroom_list)

                if sub == "Legend":
                    # 随机选择一个群聊 ID
                    chatroom_id = random.choice(chatroom_list['id'])
                    bot.sendMsg(f"已发送邀请链接，请点击链接加入群聊:", msg.sender)
                    bot.invite_chatroom_members(chatroom_id, [msg.sender])
                    return

                if sub == "群聊列表":
                    res = '所有群聊列表\n'
                    # 编号(从1开始)+简介
                    for i, chatroom in enumerate(chatroom_list):
                        res += f"{i+1}. {chatroom['description']}\n"
                    bot.sendMsg(res, msg.sender)
                    return

                # 检查群聊是否在白名单中
                try:
                    chatroom_id = chatroom_list[int(sub)]
                except:
                    bot.sendMsg('命令格式出错', msg.sender)
                    return
                # 获取群聊邀请链接
                bot.sendMsg(f"加群邀请已发送", msg.sender)
                bot.invite_chatroom_members(chatroom_id['id'], [msg.sender])
                return

        except Exception as e:
            logger.error(f"发送群聊邀请链接失败: {e}")
            logger.error(traceback.format_exc())
            bot.sendMsg("发送群聊邀请链接失败，请检查日志", msg.sender)