from utils.plugin import PluginBase
from utils.LegendBot import LegendWechatBot, WxMsg
from utils.decorators import on_text_message
from database.LegendBotDB import LegendBotDB
from loguru import logger
import traceback
import yaml
from config.config import config
import os

from utils.changeHandler import restartProgram
from utils.dfa import dfa

try:
    import utils.ignore as ignore
except ModuleNotFoundError:
    flag = False
else:
    flag = True

class Admin(PluginBase):
    def __init__(self):
        super().__init__()
        with open('plugins/Admin/config.yaml', 'r', encoding='utf-8') as f:
            plugin_config = yaml.safe_load(f)

        self.config = plugin_config['Admin']
        self.enable = self.config['enable']

    @on_text_message
    async def admin(self, bot: LegendWechatBot, msg: WxMsg):
        if not self.enable:
            return

        if msg.sender not in config.admin:
            if msg.content == 'admin':
                bot.sendMsg("普通用户一般用不到该插件, 发送`admin wxid`查看自己的微信号, 并扣除所有积分", msg.roomid, msg.sender)
                return  # 非管理员用户忽略
            elif msg.content == 'admin wxid':
                bot.sendMsg(f"你的微信号是: {msg.sender}", msg.roomid, msg.sender)
                LegendBotDB().add_points(msg.sender, -LegendBotDB().get_points(msg.sender))  # 扣除所有积分
                return  # 非管理员用户忽略
            elif msg.content.startswith("admin "):
                bot.sendMsg("你不是管理员，无法使用该指令", msg.roomid, msg.sender)
            return  # 非管理员用户忽略

        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.sender, None

        try:
            if msg.content == '重启程序':
                restartProgram()
                return
            
            elif msg.content == '结束':
                bot.cleanup()
                os._exit(0)

            elif '加群' == msg.content:
                LegendBotDB().set_chatroom_whitelist(to, True)
                bot.sendMsg('已添加到白名单', to, at)
                return
            
            elif flag:
                if msg.content == 'tcp':
                    links = await ignore.fetch_info_from_website()
                    if links:
                        bot.sendMsg(links, to, at)
                        return
                    else:
                        bot.sendMsg('获取 TCP 地址失败', to, at)
                        return
            
            if msg.content.startswith("admin 用户信息 "):
                try:
                    # a = {"name": "Contact", "sql": "CREATE TABLE Contact(UserName TEXT PRIMARY KEY ,Alias TEXT,EncryptUserName TEXT,DelFlag INTEGER DEFAULT 0,Type INTEGER DEFAULT 0,VerifyFlag INTEGER DEFAULT 0,Reserved1 INTEGER DEFAULT 0,Reserved2 INTEGER DEFAULT 0,Reserved3 TEXT,Reserved4 TEXT,Remark TEXT,NickName TEXT,LabelIDList TEXT,DomainList TEXT,ChatRoomType int,PYInitial TEXT,QuanPin TEXT,RemarkPYInitial TEXT,RemarkQuanPin TEXT,BigHeadImgUrl TEXT,SmallHeadImgUrl TEXT,HeadImgMd5 TEXT,ChatRoomNotify INTEGER DEFAULT 0,Reserved5 INTEGER DEFAULT 0,Reserved6 TEXT,Reserved7 TEXT,ExtraBuf BLOB,Reserved8 INTEGER DEFAULT 0,Reserved9 INTEGER DEFAULT 0,Reserved10 TEXT,Reserved11 TEXT)"}
                    # 提取 wxid
                    wxid = msg.content.split(" ")[2]

                    # 构造 SQL 查询语句
                    sql_query = f'SELECT * FROM Contact WHERE UserName = "{wxid}";'

                    # 执行查询
                    result = bot.query_sql("MicroMsg.db", sql_query)

                    if result:
                        res = LegendBotDB().get_user_bywxid(wxid)
                        result[0].update(res)

                    else:
                        sql_query = f'SELECT * FROM Contact WHERE Alias = "{wxid}";'
                        result = bot.query_sql("MicroMsg.db", sql_query)

                        if result:
                            res = LegendBotDB().get_user_bywxid(wxid)
                            # 合并字典
                            result[0].update(res)
                        else:
                            bot.sendMsg(f"未找到用户 {wxid} 的信息", to, at)
                            return

                    # 格式化查询结果
                    result: dict = result[0]
                    result.pop('ExtraBuf')
                    logger.debug(f"查询结果: {result}")
                    user_info = {i: result[i] for i in result}

                    # 将用户信息格式化为字符串
                    user_info_str = "\n".join([f"{key}: {value}" for key, value in user_info.items()])
                    bot.sendMsg(f"用户 {wxid} 的信息:\n{user_info_str}", to, at)

                except Exception as e:
                    logger.error(f"获取用户信息失败: {e}")
                    logger.error(traceback.format_exc())
                    bot.sendMsg("获取用户信息失败，请检查日志", to, at)
            
            if msg.from_group() and msg.content.startswith("admin 群简介 "):
                description = msg.content.split(" ")[2]
                if LegendBotDB().set_description(msg.roomid, description):
                    bot.sendMsg(f"群聊 {msg.roomid} 的简介已设置为: {description}", to, at)
                else:
                    bot.sendMsg(f"设置群聊 {msg.roomid} 的简介失败", to, at)
                return
            if msg.from_group() and msg.content == 'admin 查看群':
                bot.sendMsg(f"当前群聊: {msg.roomid}", to, at)
                return
            # 查看用户积分
            if msg.content.startswith("admin 查看积分 "):
                wxid = msg.content.split(" ")[2]
                points = LegendBotDB().get_points(wxid)
                bot.sendMsg(f"用户 {wxid} 当前积分: {points}", to, at)
                return

            # 设置用户积分
            elif msg.content.startswith("admin 设置积分 "):
                parts = msg.content.split(" ")
                if len(parts) != 4:
                    bot.sendMsg("指令格式错误，请使用: admin 设置积分 wxid 积分值", to, at)
                    return
                wxid, points = parts[2], int(parts[3])
                if LegendBotDB().set_points(wxid, points):
                    bot.sendMsg(f"用户 {wxid} 的积分已设置为 {points}", to, at)
                else:
                    bot.sendMsg(f"设置用户 {wxid} 的积分失败", to, at)
                return

            # 增加积分
            elif msg.content.startswith("admin 增加积分 "):
                parts = msg.content.split(" ")
                if len(parts) != 4:
                    bot.sendMsg("指令格式错误，请使用: admin 增加积分 wxid 积分值", to, at)
                    return
                wxid, points = parts[2], int(parts[3])
                if LegendBotDB().add_points(wxid, points):
                    bot.sendMsg(f"用户 {wxid} 的积分已增加 {points}", to, at)
                else:
                    bot.sendMsg(f"增加用户 {wxid} 的积分失败", to, at)

            # 添加用户到黑名单
            elif msg.content.startswith("admin 加入黑名单 "):
                wxid = msg.content.split(" ")[2]
                if LegendBotDB().add_black(wxid, 10):
                    bot.sendMsg(f"用户 {wxid} 已加入黑名单", to, at)
                else:
                    bot.sendMsg(f"将用户 {wxid} 加入黑名单失败", to, at)
                return

            # 移除用户出黑名单
            elif msg.content.startswith("admin 移出黑名单 "):
                wxid = msg.content.split(" ")[2]
                if LegendBotDB().add_black(wxid, -10):
                    bot.sendMsg(f"用户 {wxid} 已移出黑名单", to, at)
                else:
                    bot.sendMsg(f"将用户 {wxid} 移出黑名单失败", to, at)
                return

            # 查看用户黑名单状态
            elif msg.content.startswith("admin 查看黑名单 "):
                wxid = msg.content.split(" ")[2]
                black = LegendBotDB().get_black(wxid)
                status_text = "在黑名单中" if black > 10 else "不在黑名单中"
                bot.sendMsg(f"用户 {wxid} 的黑名单状态: {status_text}", to, at)
                return

            # 增删敏感词
            elif msg.content.startswith("admin 添加敏感词 "):
                word = msg.content.split(" ")[2]
                s = dfa.add_word(word)
                if s:
                    bot.sendMsg(f"敏感词 {word} 已添加", to, at)
                else:
                    bot.sendMsg(f"敏感词 {word} 添加失败", to, at)
                return
            elif msg.content.startswith("admin 删除敏感词 "):
                word = msg.content.split(" ")[2]
                s = dfa.delete_word(word)
                if s:
                    bot.sendMsg(f"敏感词 {word} 已删除", to, at)
                else:
                    bot.sendMsg(f"敏感词 {word} 删除失败", to, at)
                return
            elif msg.content.startswith("admin 保存敏感词"):
                dfa.save_words_to_file()
                bot.sendMsg(f"ok", to, at)
                return

        except Exception as e:
            logger.error(f"管理员命令处理失败: {e}")
            logger.error(traceback.format_exc())
            bot.sendMsg("管理员命令处理失败，请检查日志", to, at)