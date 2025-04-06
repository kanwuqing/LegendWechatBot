from config.config import config
from loguru import logger
import asyncio
from utils.LegendBot import LegendBot, LegendWechatBot
import json
import os
from database import *
from utils.decorators import scheduler
from utils.plugin import pluginManager
from queue import Empty
import psutil
import signal


async def run():
    #*================== 初始化Wcferry服务 ===================*#
    bot = LegendWechatBot()
    bot.LOG = logger

    logger.success("WechatAPI服务启动成功")

    # 已登录

    logger.success('登录成功')
    logger.info(f"登录账号信息: wxid: {bot.self_wxid}")

    #*==================== 登录完毕 初始化 =====================*#
    legendBot = LegendBot(bot)

    LegendBotDB(True) # 机器人数据库初始化不可异步
    await MessageDB().initialize()
    logger.success("数据库初始化完成")

    scheduler.start()
    logger.success("定时任务初始化完成")

    loaded_plugins = await pluginManager.load_plugins_from_directory(bot, load_disabled_plugin=False)
    logger.success(f"已加载插件: {loaded_plugins}")

    #*===================== 开始接收消息 ======================*#
    
    bot.enable_receiving_msg()

    def signal_handler(signum, frame):
        logger.info("收到终止信号，正在关闭...")
        bot.cleanup()
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    logger.success("开始接收消息")
    while bot.is_receiving_msg():
        if not psutil.sensors_battery().power_plugged:
            logger.info("电源被拔出, 停止接收消息")
            for admin in config.admin:
                bot.sendMsg('电源被拔出, 停止接收消息', admin)
                bot.cleanup()
                os._exit(0)
        try:
            msg = bot.get_msg()
            asyncio.create_task(legendBot.process_message(msg))
        except Empty:
            await asyncio.sleep(0.5)
            continue
        except Exception as e:
            logger.warning("获取新消息失败 {}", e)
            await asyncio.sleep(5)
            continue
        finally:
            await asyncio.sleep(0.5)