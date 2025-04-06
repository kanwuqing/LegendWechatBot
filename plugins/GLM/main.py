import traceback
import yaml

from loguru import logger
import os
import shutil
from wcferry import WxMsg
from utils.LegendBot import LegendWechatBot
from utils.decorators import on_text_message
from utils.plugin import PluginBase
import base64
from pathlib import Path
from database.LegendBotDB import LegendBotDB
from utils.asyncEnsure import sem
import aiohttp
import requests
from queue import Queue, Empty
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import time
import signal


class GLMPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        if not os.path.exists("plugins/GLM/config.yaml"):
            shutil.copyfile("plugins/GLM/config.yaml.example", "plugins/GLM/config.yaml")
        
        with open("plugins/GLM/config.yaml", "rb") as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config["GLM"]

        self.enable = config["enable"],
        self.folder = config["folder"]

        self.folder = os.path.join(os.path.dirname(__file__), self.folder)
        # logger.debug(self.folder)
        
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        
        if self.enable:
            self.key = config["api_key"]
            self.model = config["model"]
            # self.client = zhipuai.ZhipuAI(api_key=self.key)
            self.message_queue = Queue()
            self.img_executor = ThreadPoolExecutor(max_workers=5)
            self.video_executor = ThreadPoolExecutor(max_workers=3)
            self.process = Thread(target=self.process_queue)
            self.process.start()
            
            signal.signal(signal.SIGINT, self.process.join)

    def process_queue(self):
        """持续处理队列中的消息"""
        while self.enable:
            try:
                # 从队列中获取消息
                message = self.message_queue.get(timeout=1)  # 等待消息，超时为 1 秒

                method = message['method']
                to, at = message['to'], message['at']
                prompt = message['prompt']
                msg = message['msg']
                bot = message['bot']
                if method == 'generate_image':
                    size = message['size']
                    # 提交任务到线程池
                    self.img_executor.submit(self.generate_image, bot, prompt, size, to, at, msg)
                    self.message_queue.task_done()  # 标记任务完成
                
                else:
                    audio = message['audio']
                    base = message['base']
                    self.video_executor.submit(self.generate_video, bot, prompt, audio, base, to, at, msg)
                    self.message_queue.task_done()  # 标记任务完成
            
            except Empty:
                pass

            except Exception:
                pass

    
    def generate_image(self, bot: LegendWechatBot, prompt, size, to, at, msg: WxMsg):
        """生成图片"""
        try:
            LegendBotDB().set_running(msg.sender, True)
            logger.debug(f"生成图片: {prompt}")
            api_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
            payload = {
                "model": "cogview-3-flash",  # 确保模型名称正确
                "prompt": prompt,        # 确保输入内容符合要求
                "size": size,  # 确保尺寸符合要求
            }
            headers = {
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Connection": "close",  # 显式关闭连接
            }

            # 同步请求
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            logger.debug(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                bot.send_image(result['data'][0]['url'], to)
                LegendBotDB().set_running(msg.sender, False)
                LegendBotDB().add_points(msg.sender, -4)
            else:
                logger.error(f"API 请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
                LegendBotDB().set_running(msg.sender, False)
        except Exception as e:
            logger.error(f"调用 API 时发生错误: {e}")
            logger.error(traceback.format_exc())

    def generate_video(self, bot: LegendWechatBot, prompt, audio, base, to, at, msg: WxMsg):
        """生成视频"""
        try:
            LegendBotDB().set_running(msg.sender, True)
            logger.debug(f"生成视频: {prompt}")
            api_url = "https://open.bigmodel.cn/api/paas/v4/videos/generations"
            payload = {
                "model": "cogvideox-flash",  # 确保模型名称正确
                "prompt": prompt,        # 确保输入内容符合要求
                "with_audio": True if audio == '1' else False,
                "image_url": base
            }
            headers = {
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Connection": "close",  # 显式关闭连接
            }
            rsp = requests.post(api_url, json=payload, headers=headers, timeout=30)
            if rsp.status_code == 200:
                rsp = rsp.json()
            else:
                logger.error(f"API 请求失败，状态码: {rsp.status_code}, 错误信息: {rsp.text}")
                LegendBotDB().set_running(msg.sender, False)
                return
            task_id = rsp['id']
            api_url = f'https://open.bigmodel.cn/api/paas/v4/async-result/{task_id}'
            payload = {
                "id": task_id,
            }
            status = requests.get(api_url, json=payload, headers=headers, timeout=30)
            if status.status_code == 200:
                status = status.json()
            else:
                logger.error(f"API 请求失败，状态码: {status.status_code}, 错误信息: {status.text}")
                LegendBotDB().set_running(msg.sender, False)
                return
            while status['task_status'] != 'SUCCESS':
                time.sleep(5)
                status = requests.get(api_url, json=payload, headers=headers, timeout=30)
                if status.status_code == 200:
                    status = status.json()
                else:
                    logger.error(f"API 请求失败，状态码: {status.status_code}, 错误信息: {status.text}")
                    LegendBotDB().set_running(msg.sender, False)
                    return
            
            bot.send_image(status['video_result'][0]['url'], to)
            LegendBotDB().set_running(msg.sender, False)
            LegendBotDB().add_points(msg.sender, -5)

        except Exception as e:
            logger.error(f"调用 API 时发生错误: {e}")
            logger.error(traceback.format_exc())
        
    async def GLM_V4(self, base, mode):
        """调用视频生成 API"""
        async with sem['GLM-4V-Flash']:  # 使用信号量限制并发
            try:
                async with aiohttp.ClientSession() as session:
                    # 假设视频生成 API 的 URL 和请求格式如下
                    api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                        
                    if mode == 'video':
                        payload = {
                            'model': 'glm-4v-flash',
                            'messages': [
                                {
                                    "role": "user",
                                    "content": [
                                    {
                                        "type": "video_url",
                                        "video_url": {
                                            "url" : base
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": "请仔细描述这个视频"
                                    }
                                    ]
                                }
                            ]
                        }
                    else:
                        payload = {
                            'model': 'glm-4v-flash',
                            'messages': [
                                {
                                    "role": "user",
                                    "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url" : base
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": "请仔细描述这个视频"
                                    }
                                    ]
                                }
                            ]
                        }
                        
                    headers = {
                        "Authorization": f"Bearer {self.key}",
                        "Content-Type": "application/json",
                        "Connection": "close",  # 显式关闭连接
                    }

                    async with session.post(api_url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result
                        else:
                            logger.error(f"API 请求失败，状态码: {response.status}, {response.text()}")
                            return None
            except Exception as e:
                logger.error(f"调用 API 时发生错误: {e}")
                logger.error(traceback.format_exc())

    @on_text_message
    async def glm(self, bot: LegendWechatBot, msg: WxMsg):
        if not self.enable:
            return
        
        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.sender, None

        if msg.content == 'glm':
            bot.sendMsg('GLM插件相关命令:\n`glm v4`图像视频理解相关功能, 3积分/次\n`glm img`图片生成相关功能, 4积分/次\n`glm video`视频生成相关功能, 5积分/次', to, at)
        
        try:
            #* 理解(OK)
            if msg.content.startswith('glm v4'):
                #* 说明
                if msg.content == 'glm v4':
                    bot.sendMsg('图像视频理解相关功能\n`glm v4 local 多媒体名`传入本地多媒体\n`glm v4 url 链接`传入网络多媒体', to, at)
                    return
                
                model = 'v4'

                #* 本地多媒体
                if msg.content.startswith('glm v4 local '):
                    image = msg.content.split(' ')[3]
                    image = os.path.basename(image)
                    img: Path = Path().cwd() / 'plugins/ImageDeal/images' / msg.sender / image
                    if not img.exists():
                        bot.sendMsg('多媒体不存在', to, at)
                        return
                    
                    if img.suffix == '.mp4':
                        mode = 'video'
                    else:
                        mode = 'image'
                    
                    LegendBotDB().set_running(msg.sender, True)
                    with open(img, 'rb') as f:
                        base = base64.b64encode(f.read()).decode('utf-8')

                    rsp = await self.GLM_V4(base, mode)

                    if rsp:

                        bot.sendMsg(rsp.get('choices')[0].get('message').get('content'), to, at)
                    else:
                        bot.sendMsg('请求失败', to, at)

                    LegendBotDB().add_points(msg.sender, -3)
                    LegendBotDB().set_running(msg.sender, False)
                    return
                
                #* 网络链接
                elif msg.content.startswith('glm v4 url '):
                    url = msg.content.split(' ')[3]
                    mode = 'video' if (url.endswith('.mp4') or url.endswith('.wav')) else 'image'

                    LegendBotDB().set_running(msg.sender, True)
                    rsp = await self.client.chat.completions.create(
                        model=self.model[model],
                        messages=[
                            {
                            "role": "user",
                            "content": [
                                {
                                    "type": f"{mode}_url",
                                    f"{mode}_url": {
                                        "url": url
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": "请描述这个图片" if mode == 'image' else "请描述这个视频"
                                }
                            ]
                            }
                        ]
                    )

                    bot.sendMsg(rsp.choices[0].message.content, to, at)
                    LegendBotDB().add_points(msg.sender, -3)
                    LegendBotDB().set_running(msg.sender, False)
                    return
            
            #* 图片生成
            if msg.content.startswith('glm img'):
                #* 说明
                if msg.content == 'glm img':
                    bot.sendMsg('图片生成相关功能\n`glm img 要求 尺寸\n其中尺寸可在以下范围中选择:1024x1024,768x1344,864x1152,1344x768,1152x864,1440x720,720x1440, 默认为1024x1024`', to, at)
                    return

                if msg.content.startswith('glm img '):
                    msg.content = msg.content[8:]
                    if msg.content.count(' ') == 1:
                        prompt, size = msg.content.split(' ')
                    else:
                        prompt = msg.content
                        size = '1024x1024'
                    
                    if size not in ['1024x1024', '768x1344', '864x1152', '1344x768', '1152x864', '1440x720', '720x1440']:
                        size = '1024x1024'
                    
                    self.message_queue.put({
                        "bot": bot,
                        "prompt": prompt,
                        "size": size,
                        "method": "generate_image",
                        "to": to,
                        "at": at,
                        'msg': msg
                    })
                    bot.sendMsg("已接收图片生成请求，正在处理...", to, at)
                    return
            
            #* 视频生成
            if msg.content.startswith("glm video"):
                # 将消息添加到队列
                #* 说明
                if msg.content == "glm video":
                    bot.sendMsg(
                        "视频生成相关功能\n"
                        "`glm video 要求 --audio 音频需求 --mode local/url 图片基础`\n"
                        "音频需求可选择1或0, 1为需要音频, 0为不需要音频, 默认为0\n"
                        "若有视频创作的图片基础, 则选择local(本地)或url(网络链接), 图片基础部分与`glm v4`格式相同, 默认无基础",
                        to,
                        at,
                    )
                    return

                try:
                    # 解析指令内容
                    msg.content = msg.content[10:]  # 去掉 "glm video " 前缀
                    parts = msg.content.split(" ")

                    # 默认值
                    prompt = parts[0]  # 视频生成的要求
                    audio = "0"  # 默认不需要音频
                    base_type = None
                    base_value = None

                    # 解析参数
                    if "--audio" in parts:
                        audio_index = parts.index("--audio") + 1
                        if audio_index < len(parts):
                            audio = parts[audio_index]

                    if "--mode" in parts:
                        mode_index = parts.index("--mode") + 1
                        if mode_index < len(parts):
                            base_type = parts[mode_index]
                            if base_type not in ["local", "url"]:
                                bot.sendMsg("模式参数错误，请选择 local 或 url", to, at)
                                return

                            # 获取图片基础
                            base_value_index = mode_index + 1
                            if base_value_index < len(parts):
                                base_value = parts[base_value_index]
                    
                    logger.debug(f"解析指令: prompt={prompt}, audio={audio}, base_type={base_type}, base_value={base_value}")

                    # 检查图片基础部分
                    if base_type == "local":
                        base_path = os.path.basename(base_value)
                        img: Path = Path().cwd() / "plugins/ImageDeal/images" / msg.sender / base_path
                        if not img.exists():
                            bot.sendMsg("本地图片基础不存在", to, at)
                            return
                        with open(img, "rb") as f:
                            base = base64.b64encode(f.read()).decode("utf-8")
                    elif base_type == "url":
                        base = base_value
                    else:
                        base = None

                    # 将消息添加到队列
                    self.message_queue.put(
                        {
                            "bot": bot,
                            "prompt": prompt,
                            "audio": audio,
                            "base": base,
                            "method": "generate_video",
                            "to": to,
                            "at": at,
                            'msg': msg
                        }
                    )
                    bot.sendMsg("已接收视频生成请求，正在处理...", to, at)

                except Exception as e:
                    logger.error(f"解析指令时发生错误: {e}")
                    logger.error(traceback.format_exc())
                    bot.sendMsg("指令解析失败，请检查格式是否正确", to, at)
                    

        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            LegendBotDB().set_running(msg.sender, False)
            bot.sendMsg('发生错误', to, at)