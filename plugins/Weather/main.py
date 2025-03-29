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


class Weather(PluginBase):

    def __init__(self):
        super().__init__()
        if not os.path.exists("plugins/Weather/config.yaml"):
            shutil.copyfile("plugins/Weather/config.yaml.example", "plugins/Weather/config.yaml")

        with open("plugins/Weather/config.yaml", "rb") as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config["Weather"]
        self.enable = config["enable"]

        if self.enable:
            self.key = config["key"]
            if not os.path.exists("plugins/Weather/subs.json"):
                with open('plugins/Weather/subs.json', 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                    self.subs = {}
            
            else:
                with open('plugins/Weather/subs.json', 'r', encoding='utf-8') as f:
                    self.subs = json.load(f)

    
    @on_text_message
    async def weather(self, bot: LegendWechatBot, msg: WxMsg):
        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.sender, None
        
        if not self.enable:
            return
        
        if msg.content.startswith("天气"):
            if msg.content == '天气':
                bot.sendMsg("天气查询功能, 每次查询消耗1积分\n命令格式: `天气 国内城市名 天数(只需一个数字, 0~2, 0代表今天, 默认为0)`\n天气预报定点发送命令: `天气 预报 城市`, 仅限群聊使用, 一个群聊最多预报5个城市\n取消订阅城市命令: `天气 td 城市`", to, at)
                return
            
            try:
                msg.content = msg.content[3:]
                if msg.content.startswith("预报 ") and msg.from_group():
                    city = msg.content[3:]

                    async with aiohttp.ClientSession() as session:
                        url = f"https://api.seniverse.com/v3/weather/daily.json?key={self.key}&location={city}&language=zh-Hans&unit=c"
                        async with session.get(url) as resp:
                            if resp.status != 200:
                                logger.warning(f"天气查询失败: {resp.status}")
                                return
                            rsp1 = await resp.json()
                    
                    if 'status_code' in rsp1 and rsp1['status_code'] == "AP010006":
                        bot.sendMsg("城市名错误, 请重新输入", to, at)
                        return

                    if to in self.subs:
                        if city in self.subs[to]:
                            bot.sendMsg("该城市已订阅, 请勿重复订阅", to, at)
                            return
                        if len(self.subs[to]) > 5:
                            bot.sendMsg("该群聊已订阅5个城市, 请先取消订阅", to, at)
                            return

                        self.subs[to].append(city)
                        with open('plugins/Weather/subs.json', 'w', encoding='utf-8') as f:
                            json.dump(self.subs, f, ensure_ascii=False, indent=4)
                        bot.sendMsg("订阅成功", to, at)
                        return

                    self.subs[to] = [city]
                
                elif msg.content.startswith("td "):
                    city = msg.content[3:]
                    if to in self.subs:
                        if city in self.subs[to]:
                            self.subs[to].remove(city)
                            with open('plugins/Weather/subs.json', 'w', encoding='utf-8') as f:
                                json.dump(self.subs, f, ensure_ascii=False, indent=4)
                            bot.sendMsg("取消订阅成功", to, at)
                            return
                        else:
                            bot.sendMsg("该城市未订阅, 请先订阅", to, at)
                            return
                    else:
                        bot.sendMsg("该群聊未订阅任何城市, 请先订阅", to, at)
                        return

                else:
                    if msg.content.count(' ') == 1:
                        city, day = msg.content.split(' ')
                    else:
                        city, day = msg.content, 0
                    if day >= 3:
                        return
                    
                    async with aiohttp.ClientSession() as session:
                        url = f"https://api.seniverse.com/v3/weather/daily.json?key={self.key}&location={city}&language=zh-Hans&unit=c"
                        async with session.get(url) as resp:
                            if resp.status != 200:
                                logger.warning(f"天气查询失败: {resp.status}")
                                return
                            rsp1 = await resp.json()
                    
                    if 'status_code' in rsp1 and rsp1['status_code'] == "AP010006":
                        bot.sendMsg("城市名错误, 请重新输入", to, at)
                        return
                    
                    rsp = rsp1["results"][0]["daily"][day]
                    upd = rsp1['results'][0]['last_update']
                    res = f"{city}{rsp['date']}天气, 更新于{upd}\n白天天气:{rsp['text_day']}, 夜间天气:{rsp['text_night']}\n最高温: {rsp['high']}, 最低温: {rsp['low']}\n降水概率: {rsp['precip']}%, 湿度: {rsp['humidity']}\n风力风向: {rsp['wind_direction']}风{rsp['rainfall']}级, 风速: {rsp['wind_speed']}"

                    bot.sendMsg(res, to, at)
                    LegendBotDB().add_points(msg.sender, -1)
                
            except:
                logger.debug(f"天气查询失败: {traceback.format_exc()}")
                return
    

    @schedule('cron', hour=21, minute=24, second=0, misfire_grace_time=None)
    async def send_weather(self, bot: LegendWechatBot):
        for to in self.subs:
            for city in self.subs[to]:
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.seniverse.com/v3/weather/daily.json?key={self.key}&location={city}&language=zh-Hans&unit=c"
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            logger.warning(f"天气查询失败: {resp.status}")
                            continue
                        rsp1 = await resp.json()
                
                rsp = rsp1["results"][0]["daily"][1]
                upd = rsp1['results'][0]['last_update']
                res = f"{city}{rsp['date']}天气, 更新于{upd}\n白天天气:{rsp['text_day']}, 夜间天气:{rsp['text_night']}\n最高温: {rsp['high']}, 最低温: {rsp['low']}\n降水概率: {rsp['precip']}%, 湿度: {rsp['humidity']}\n风力风向: {rsp['wind_direction']}风{rsp['rainfall']}级, 风速: {rsp['wind_speed']}"

                bot.sendMsg(res, to)
