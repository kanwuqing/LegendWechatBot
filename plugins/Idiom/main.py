import pandas as pd
import os
import random
from database.LegendBotDB import LegendBotDB

class Chengyu(object):
    def __init__(self) -> None:
        self.df = pd.read_csv(f"idiom.csv", delimiter="\t")
        self.cys, self.zis, self.yins = self._build_data()

    def _build_data(self):
        df = self.df.copy()
        df["shouzi"] = df["chengyu"].apply(lambda x: x[0])
        df["mozi"] = df["chengyu"].apply(lambda x: x[-1])

        df["shouyin"] = df["pingyin"].apply(lambda x: x.split(" ")[0])
        df["moyin"] = df["pingyin"].apply(lambda x: x.split(" ")[-1])

        cys = dict(zip(df["chengyu"], df["moyin"]))
        zis = df.groupby("shouzi").agg({"chengyu": set})["chengyu"].to_dict()
        yins = df.groupby("shouyin").agg({"chengyu": set})["chengyu"].to_dict()

        return cys, zis, yins

    def isChengyu(self, cy: str) -> bool:
        return self.cys.get(cy, None) is not None

    def getNext(self, cy: str, tongyin: bool = True) -> str:
        """获取下一个成语
            cy: 当前成语
            tongyin: 是否允许同音字
        """
        zi = cy[-1]
        ansers = list(self.zis.get(zi, {}))
        try:
            ansers.remove(cy)  # 移除当前成语
        except Exception as e:
            pass  # Just ignore...

        if ansers:
            return random.choice(ansers)

        # 如果找不到同字，允许同音
        if tongyin:
            yin = self.cys.get(cy)
            ansers = list(self.yins.get(yin, {}))

        try:
            ansers.remove(cy)  # 移除当前成语
        except Exception as e:
            pass  # Just ignore...

        if ansers:
            return random.choice(ansers)

        return None

    def getMeaning(self, cy: str) -> str:
        ress = self.df[self.df["chengyu"] == cy].to_dict(orient="records")
        if ress:
            res = ress[0]
            rsp = res["chengyu"] + "\n" + res["pingyin"] + "\n" + res["jieshi"]
            if res["chuchu"] and res["chuchu"] != "无":
                rsp += "\n出处：" + res["chuchu"]
            if res["lizi"] and res["lizi"] != "无":
                rsp += "\n例子：" + res["lizi"]
            return rsp
        return None

import traceback
from loguru import logger
from utils.LegendBot import LegendWechatBot, WxMsg
from utils.decorators import on_text_message
from utils.plugin import PluginBase

class Idiom(PluginBase):
    def __init__(self):
        super().__init__()
        self.chengyu = Chengyu()  # 初始化成语工具类
        self.enable = True  # 插件默认启用

    @on_text_message
    async def handle_idiom(self, bot: LegendWechatBot, msg: WxMsg):
        if not self.enable:
            return

        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.sender, None

        try:
            if msg.content == "成语":
                bot.sendMsg(
                    "成语插件相关命令:\n"
                    "`成语查询 成语` - 查询成语的详细信息\n"
                    "`成语接龙 成语` - 根据输入的成语进行接龙\n"
                    "`成语帮助` - 查看帮助信息",
                    to,
                    at,
                )
                return
            # 成语查询功能
            if msg.content.startswith("成语查询 "):
                idiom = msg.content[5:]
                if not self.chengyu.isChengyu(idiom):
                    bot.sendMsg(f"未找到成语: {idiom}", to, at)
                    return

                meaning = self.chengyu.getMeaning(idiom)
                if meaning:
                    bot.sendMsg(meaning, to, at)
                else:
                    bot.sendMsg(f"未找到成语 {idiom} 的详细信息", to, at)
                return

            # 成语接龙功能
            elif msg.content.startswith("成语接龙 "):
                idiom = msg.content[5:]
                if not self.chengyu.isChengyu(idiom):
                    bot.sendMsg(f"未找到成语: {idiom}", to, at)
                    return

                next_idiom = self.chengyu.getNext(idiom)
                if next_idiom:
                    bot.sendMsg(f"接龙成语: {next_idiom}", to, at)
                else:
                    bot.sendMsg(f"未找到可以接龙的成语", to, at)
                return

            # 成语帮助功能
            elif msg.content == "成语帮助":
                bot.sendMsg(
                    "成语插件相关命令:\n"
                    "`成语查询 成语` - 查询成语的详细信息\n"
                    "`成语接龙 成语` - 根据输入的成语进行接龙\n"
                    "`成语帮助` - 查看帮助信息",
                    to,
                    at,
                )
                return

        except Exception as e:
            logger.error(f"处理成语命令时发生错误: {e}")
            logger.error(traceback.format_exc())
            bot.sendMsg("处理成语命令时发生错误，请检查日志", to, at)