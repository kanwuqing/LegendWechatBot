import yaml
import openai
import os
import shutil
from loguru import logger
from utils.decorators import on_text_message
from utils.plugin import PluginBase
from utils.LegendBot import LegendWechatBot
from wcferry import WxMsg
import traceback
from utils.asyncEnsure import sem
from database.LegendBotDB import LegendBotDB

class AI(PluginBase):

    def __init__(self):
        super().__init__()
        # 检查配置文件是否存在
        if not os.path.exists("plugins/AI/config.yaml"):
            shutil.copyfile("plugins/AI/config.yaml.example", "plugins/AI/config.yaml")

        # 加载配置文件
        with open("plugins/AI/config.yaml", "rb") as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config["AI"]
        self.models = config['models']
        self.enable = config["enable"]

        if self.enable:
            self.key = config["api_key"]
            self.base_url = config["url"]
        
        self.client = openai.AsyncOpenAI(api_key=self.key, base_url=self.base_url)

    @on_text_message
    async def query_AI(self, bot: LegendWechatBot, msg: WxMsg):
        """处理用户发送的 OpenAI 查询命令"""
        if not self.enable:
            return
        
        async with sem['processAI']:

            if msg.from_group():
                to, at = msg.roomid, msg.sender
            else:
                to, at = msg.sender, None

            if msg.content.startswith("ai"):
                if msg.content == 'ai':
                    bot.sendMsg("与AI对话, 每次消耗3积分, 命令格式: `ai 模型名称(默认为deepseek V3) 内容`\n目前支持的模型:\n1.v3(deepseekV3), r1(deepseekR1)", to, at)
                    return
                
                query = msg.content[3:]

                if query.count(' ') == 1:
                    model, query = query.split(' ')
                
                else:
                    model = "v3"

                try:
                    LegendBotDB().set_running(msg.sender, True)
                    # 调用 OpenAI API
                    logger.debug(model)
                    response = await self.client.chat.completions.create(
                        model=self.models[model],  # 使用的模型
                        messages=[
                            # {"role": "system", "content": "你是一个帮助用户回答问题的助手。"},
                            {"role": "user", "content": query}
                        ],
                    )

                    logger.debug('AI已返回')

                    # 获取 API 返回的内容
                    result = response.choices[0].message.content.replace("\\n", "\n")

                    # 发送结果给用户
                    bot.sendMsg(f"{result}", to, at)
                    LegendBotDB().set_running(msg.sender, False)
                    LegendBotDB().add_points(msg.sender, -3)

                except Exception as e:
                    logger.error(f"调用 OpenAI API 时发生错误: {e}")
                    logger.error(traceback.format_exc())
                    LegendBotDB().set_running(msg.sender, False)