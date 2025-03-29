import random
from utils.plugin import PluginBase
import yaml
import datetime
from database.LegendBotDB import LegendBotDB
from utils.LegendBot import LegendWechatBot, WxMsg
from utils.decorators import on_text_message
from config.config import config
from loguru import logger
import traceback

class SignUp(PluginBase):
    def __init__(self):
        super().__init__()
        with open('plugins/SignUp/config.yaml', 'r', encoding='utf-8') as f:
            plugin_config = yaml.safe_load(f)

        config = plugin_config['SignUp']
        self.enable = config['enable']
        self.good = config['good']
        self.good_text = config['good_text']
        self.bad = config['bad']
        self.bad_text = config['bad_text']
        self.names = config['names']
        
    def get_fortune(self):
        '''
        good = [
            ["宜:诸事皆宜","宜:诸事皆宜","宜:诸事皆宜","宜:诸事皆宜"],
            ["宜:装弱","宜:窝在家里","宜:刷题","宜:吃饭"],
            ["宜:刷题","宜:开电脑","宜:写作业","宜:睡觉"],
            ["宜:发朋友圈","宜:出去玩","宜:打游戏","宜:吃饭"],
            ["宜:学习","宜:研究Ruby","宜:研究c#","宜:玩游戏"],
            ["宜:膜拜大神","宜:扶老奶奶过马路","宜:玩网游","宜:喝可乐"],
            ["宜:吃东西","宜:打sdvx","宜:打开洛谷","宜:出行"],
            ["宜:写程序","宜:刷题","宜:偷塔","宜:上CSDN"],
            ["宜:扶老奶奶过马路","宜:上课","宜:写作业","宜:写程序"]
        ]
        good_text = [
            ["","","",""],
            ["谦虚最好了","不出门没有危险","直接AC","吃的饱饱的再学习"],
            ["一次AC","发现电脑死机了","全对","睡足了再学习"],
            ["点赞量破百","真开心","十连胜","吃饱了"],
            ["都会","有了新发现","发现新大陆","直接胜利"],
            ["接受神之沐浴","增加RP","犹如神助","真好喝"],
            ["吃饱了","今天状态好","发现AC的题变多了","路途顺畅"],
            ["不会报错","直接TLE","胜利","发现粉丝涨了200个"],
            ["增加RP","听懂了","都会","没有Bug"]
        ]
        bad = [
            ["忌:诸事不宜","忌:诸事不宜","忌:诸事不宜","忌:诸事不宜"],
            ["忌:打sdvx","忌:出行","忌:玩手机","忌:吃方便面"],
            ["忌:关电脑","忌:开挂","忌:纳财","忌:考试"],
            ["忌:膜拜大神","忌:评论","忌:研究Java","忌:吃方便面"],
            ["忌:发朋友圈","忌:打开洛谷","忌:研究C++","忌:出行"],
            ["忌:探险","忌:发视频","忌:发博客","忌:给别人点赞"],
            ["忌:写程序","忌:使用Unity打包exe","忌:装弱","忌:打开CSDN"],
            ["忌:点开wx","忌:刷题","忌:打吃鸡","忌:和别人分享你的程序"],
            ["忌:纳财","忌:写程序超过500行","忌:断网","忌:检测Bug"]
        ]
        bad_text = [
            ["","","",""],
            ["今天状态不好","路途也许坎坷","好家伙，直接死机","没有调味料"],
            ["死机了","被制裁","你没有财运","没及格"],
            ["被人嘲笑","被喷","心态崩溃","只有一包调味料"],
            ["被人当成买面膜的","大凶","五行代码198个报错","路途坎坷"],
            ["你失踪了","被人喷","阅读量1","被人嘲笑"],
            ["报错19999+","电脑卡死, 发现刚才做的demo全没了","被人看穿","被人陷害"],
            ["被人陷害","WA","被队友炸死","别人发现了Bug"],
            ["没有财运","99+报错","连不上了","503个Bug"],
        ]
        '''
        
        
        w_list = [3, 5, 11, 19, 20, 18, 10, 8, 4, 2]
        w_sum = 0
        for i in w_list:
            w_sum += i
        randVal = random.randint(0, w_sum)
        rward = 0
        for i in range(len(w_list)):
            if randVal <= w_list[i]:
                rward = i
                break
            randVal -= w_list[i]
        # print('§' + names[rward] + '§')
        i1 = random.randint(0, 9)
        i2 = random.randint(0, 9)
        while i1 == i2:
            i2 = random.randint(0, 9)
        i3 = random.randint(1, 8)
        i4 = random.randint(1, 8)
        while i3 == i4:
            i4 = random.randint(1, 8)
        if rward == 0 or rward == 9:
            i3 = rward
            i4 = rward
        '''
        print('宜:')
        print('1:' + good[rward][i1])
        print(good_text[rward][i1])
        print('2:' + good[rward][i2])
        print(good_text[rward][i2])
        print('忌:')
        print('1:' + bad[rward][i1])
        print(bad_text[rward][i1])
        print('2:' + bad[rward][i2])
        print(bad_text[rward][i2])
        '''
        return self.names[rward] + '$' + self.good[i3][i1] + '$' + self.good_text[i3][i1] + '$' + self.good[i3][i2] + '$' + self.good_text[i3][i2] + '$' + self.bad[i4][i1] + '$' + self.bad_text[i4][i1] + '$' + self.bad[i4][i2] + '$' + self.bad_text[i4][i2]

    def get_calender(self):
        tg='癸甲乙丙丁戊己庚辛壬'
        dz='亥子丑寅卯辰已午未申酉戌'
        month_list = [None, '一月大', '二月平', '三月大', '四月小', '五月大', '六月小',
                    '七月大', '八月大', '九月小', '十月大', '十一月小', '十二月大']
        week_list = [None, '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        date = datetime.datetime.now().date()
        year = date.year
        month = month_list[date.month]
        day = date.day
        week = week_list[date.isoweekday()]
        if week == '星期六' or week == '星期日':
            color = 'red'
        else:
            color = 'green'
        year1 = tg[(year - 3) % 10] + dz[(year - 3) % 12]
        return {'year': year, 'year1': year1, 'month': month, 'day': day, 'week': week, 'color': color}

    @on_text_message
    async def processSignMsg(self, bot: LegendWechatBot, msg: WxMsg):

        if not self.enable:
            return
        
        if msg.from_group():
            to, at = msg.roomid, msg.sender
        else:
            to, at = msg.sender, None
        
        try:
            if msg.content == '签到':
                lastSign, maxSign, fortune = LegendBotDB().get_signin_stat(msg.sender)
                if lastSign and datetime.datetime.today().date() == lastSign.date():
                    bot.sendMsg('你已经签过到了', to, at)
                    return
                else:
                    fortune = self.get_fortune()
                    lastSign = self.get_calender()
                    LegendBotDB().set_signin_stat(msg.sender, fortune)
                    _, maxSign, fortune = LegendBotDB().get_signin_stat(msg.sender)
                    fortune = fortune.split('$')

                    res = '签到成功!\n已连续签到%d天, 积分+%d, 目前积分: %d\n%s-农历%s年\n%s月%s日\n今日运势:%s\n宜:%s-%s\n宜:%s-%s\n忌:%s-%s\n忌:%s-%s\n输入`签到 查看运势/积分`可查询运势和积分' % tuple([maxSign, config.RobotConfig['signPoint'] + min(maxSign, 10), LegendBotDB().get_points(msg.sender), lastSign['year'], lastSign['year1'], lastSign["month"], lastSign["day"]] + fortune)

                    bot.sendMsg(res, to, at)
                    return
            elif msg.content == '签到 查看积分':
                bot.sendMsg('当前积分:%d' % LegendBotDB().get_points(msg.sender), to, at)
                return
            elif msg.content == '签到 查看运势':
                lastSign, maxSign, fortune = LegendBotDB().get_signin_stat(msg.sender)
                fortune = fortune.split('$')
                res = '今日运势:%s\n宜:%s-%s\n宜:%s-%s\n忌:%s-%s\n忌:%s-%s' % tuple(fortune)

                bot.sendMsg(res, to, at)
                return

        except Exception as e:
            logger.warning('签到失败: %s' % e)
            logger.error(traceback.format_exc())