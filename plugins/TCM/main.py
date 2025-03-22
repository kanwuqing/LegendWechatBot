import yaml
import xml.etree.ElementTree as ET
from datetime import datetime
import difflib
from loguru import logger

from wcferry import Wcf, WxMsg
from utils.decorators import on_text_message
from utils.plugin import PluginBase
from utils.LegendBot import LegendWechatBot
from utils.dictTools import *
from database.LegendBotDB import LegendBotDB
import traceback

class TCM(PluginBase):

    def __init__(self):
        super().__init__()

        with open("plugins/TCM/config.yaml", "rb") as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config["TCM"]
        self.enabled = config["enable"]
        self.users = {} # 正在问诊的用户
        self.tree = config['tree']
        self.prescription = config['prescription']
    
    @on_text_message
    async def TCM(self, bot: LegendWechatBot, msg: WxMsg):
        # 判断消息是否来自群聊
        if msg.from_group():
            # 如果是群聊，则将消息发送者和群聊ID赋值给to和at
            to, at = msg.roomid, msg.sender
        else:
            # 如果不是群聊，则将消息发送者赋值给to，at为None
            to, at = msg.sender, None
        
        # 如果TCM功能未启用，则直接返回
        if not self.enabled:
            return
        
        # 如果消息内容为"中药"，则发送帮助信息
        if msg.content == '中药':
            bot.sendMsg("中药药方查询, 可输入最明显症状后开始问诊\n开始问诊命令格式: '中药 症状序号', 若不确定你也可以选择输入'中药 q 主要症状', 系统会自动帮你匹配关联度最高的诊断路径(但不保证你的症状会出现在诊断过程中)\n在问诊过程中, 请按照提示回答, 提示中可能仅为部分症状, 请严格按照提示回答(符合问题中症状即可), 每次回答同样以'中药 '开头, 直到问诊结束\n返回结果: 问诊期间的问题或者最终结论(药方)\n\n目前支持的病症:\n1.感冒, 发热等 (具体症状请参见问诊过程)\n2.水肿, 咳嗽, 发热等\n3.咳嗽, 虚弱, 心悸等\n4.咽部难受, 腹泻呕吐等\n5.发热, 食欲不佳等\n\n注意事项:\n注意事项:\n1.提供的意见仅供参考, 如有不适请及时就医\n2.本项目不提供处方, 请勿用于实际治疗\n3.本项目提供的剂量仅为常用剂量, 具体剂量请根据医生建议或实际情况进行灵活调整\n\n命令示例:\n中药 -> 获取帮助信息\n中药 1 -> 查询感冒, 发热等\n中药 q 我心烦 -> 查询心烦相关的诊断路径\n中药 是 -> 在问诊过程中答案为是", to, at)
            return
        
        # 如果消息来自群聊，则直接返回
        if msg.from_group():
            return

        try:
            # 如果消息内容以"中药 "开头，则截取"中药 "后面的内容
            if msg.content.lower().startswith("中药 "):
                msg.content = msg.content[3:]
                f = 0
                # 如果消息内容为"结束"，则结束问诊
                if msg.content == '结束':
                    bot.sendMsg(f'问诊结束', to, at)
                    # 从用户字典中删除该用户
                    del self.users[msg.sender]
                    return
                try:
                    # 如果消息内容以"q "开头，则进行模糊匹配
                    if msg.content.startswith('q '):
                        # 如果该用户已经在问诊中，则发送提示信息
                        if msg.sender in self.users:
                            bot.sendMsg("你已经处于一个问诊中了, 黑名单指数+1, 请注意", to, at)
                            # 将该用户加入黑名单，黑名单指数+1
                            await LegendBotDB.add_black(wxid=msg.sender, n=1)
                            return
                            
                        # 截取"q "后面的内容
                        msg.content = msg.content[2:]
                        # 进行模糊匹配
                        paths, _ = self.find_most_similar_question(self.tree, msg.content)
                        # 如果没有找到匹配的路径，则发送提示信息
                        if not paths:
                            bot.sendMsg(f'没有找到与"{msg.content}"相关的诊断路径', to, at)
                            return
                        # 将该用户加入用户字典
                        self.users[msg.sender] = self.tree[paths[0][0]]
                        s = ""
                        # 将匹配的路径拼接成字符串
                        for path in paths:
                            s += ' -> '.join(path) + '\n'
                        s = s.strip('\n')
                        # 发送匹配的路径
                        bot.sendMsg(f"找到以下可能的诊断路径, 若系统匹配不准确, 你还可以尝试以下诊断:{s}\n", to, at)
                        # 发送提示信息
                        bot.sendMsg("问诊开始, 请按照提示回答, 回答格式: '中药 选项'", to, at)
                        f = 1
                    else:
                        # 将消息内容转换为整数
                        msg.content = int(msg.content) - 1
                        if list(self.tree.keys())[msg.content]:
                            if msg.sender in self.users:
                                bot.sendMsg("你已经处于一个问诊中了, 黑名单指数+1, 请注意", to, at)
                                await LegendBotDB.add_black(wxid=msg.sender, n=1)
                                return
                            
                            self.users[msg.sender] = self.tree[list(self.tree.keys())[msg.content]]
                            bot.sendMsg("问诊开始, 请按照提示回答, 回答格式: '中药 选项'", to, at)
                            f = 1
                except:
                    logger.debug(traceback.format_exc())
                    pass
                
                if msg.sender not in self.users:
                    return

                elif msg.content in self.users[msg.sender]:
                    self.users[msg.sender] = self.users[msg.sender][msg.content]
                
                elif f == 0:
                    return

                if isinstance(self.users[msg.sender], str):
                    title = self.users[msg.sender]
                    prescription = self.prescription[title]
                    bot.sendMsg(f'问诊结束, 药方名称: {title}, 药方内容: {prescription}', to, at)
                    if '附子' in prescription:
                        bot.sendMsg(f'注意, {title}内含有附子类风险方剂, 使用不当会导致中毒, 请谨慎使用', to, at)
                    del self.users[msg.sender]
                    return
                
                bot.sendMsg(self.users[msg.sender]['q'], to, at)
                return
        except Exception as e:
            logger.error(e)
            logger.debug(traceback.format_exc())
    
    @staticmethod
    def find_most_similar_question(tree, user_input):
        # 遍历树形结构，返回所有问题及其路径
        def traverse_tree(tree, path=[]):
            # 定义一个空列表，用于存储问题及其路径
            questions = []
            # 遍历树形结构的每个节点
            for key, value in tree.items():
                # 如果节点的值是一个字典
                if isinstance(value, dict):
                    # 如果字典中包含问题
                    if 'q' in value:
                        # 将问题及其路径添加到列表中
                        questions.append((value['q'], path + [key]))
                    # 递归调用traverse_tree函数，继续遍历子节点
                    questions.extend(traverse_tree(value, path + [key]))
            # 返回问题及其路径的列表
            return questions

        questions = traverse_tree(tree)
        question_texts = [q[0] for q in questions]
        most_similar = difflib.get_close_matches(user_input, question_texts, n=3, cutoff=0.0)
        
        paths = []
        ques = []
        if most_similar:
            for question, path in questions:
                if question in most_similar:
                    paths.append(path)
                    ques.append(question)
            return paths, ques
        return [], []