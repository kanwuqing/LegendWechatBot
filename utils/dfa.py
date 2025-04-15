import asyncio
from loguru import logger

class DFA:
    def __init__(self):
        self.ban_words_set = set()
        self.ban_words_list = []
        self.ban_words_dict = {}
        self.path = 'docs/ban.txt'
        self.get_words()

    # 获取敏感词列表
    def get_words(self):
        with open(self.path, 'r', encoding='utf-8-sig') as f:
            for s in f:
                if s.find('\\r'):
                    s = s.replace('\r', '')
                s = s.replace('\n', '')
                s = s.strip()
                if len(s) == 0:
                    continue
                if str(s) and s not in self.ban_words_set:
                    self.ban_words_set.add(s)
                    self.ban_words_list.append(str(s))
        self.add_hash_dict(self.ban_words_list)

    # 将敏感词列表转换为DFA字典序
    def add_hash_dict(self, new_list):
        for x in new_list:
            self.add_new_word(x)

    # 添加单个敏感词
    def add_new_word(self, new_word):
        new_word = str(new_word)
        now_dict = self.ban_words_dict
        i = 0
        for x in new_word:
            if x not in now_dict:
                x = str(x)
                new_dict = dict()
                new_dict['is_end'] = False
                now_dict[x] = new_dict
                now_dict = new_dict
            else:
                now_dict = now_dict[x]
            if i == len(new_word) - 1:
                now_dict['is_end'] = True
            i += 1

    # 动态添加单个敏感词
    def add_word(self, word):
        """
        动态添加单个敏感词
        """
        word = str(word).strip()
        if not word:
            logger.warning("敏感词不能为空")
            return False

        if word in self.ban_words_set:
            logger.info(f"敏感词 '{word}' 已存在")
            return False

        # 添加到敏感词集合和列表
        self.ban_words_set.add(word)
        self.ban_words_list.append(word)

        # 添加到 DFA 字典
        self.add_new_word(word)
        logger.info(f"敏感词 '{word}' 已成功添加")
        return True

    # 将敏感词写入文件
    def save_words_to_file(self):
        """
        将当前敏感词列表写入文件
        """
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                for word in self.ban_words_list:
                    f.write(word + '\n')
            logger.info(f"敏感词列表已成功写入文件: {self.path}")
        except Exception as e:
            logger.error(f"写入敏感词文件失败: {e}")
    
    # 删除单个敏感词
    def delete_word(self, word):
        """
        从 DFA 敏感词字典中删除指定的敏感词
        """
        word = str(word)
        now_dict = self.ban_words_dict
        stack = []  # 用于记录路径
        if word not in self.ban_words_list:
            logger.warning(f"敏感词 '{word}' 不存在，无法删除")
            return False
        
        self.ban_words_list.remove(word)
        self.ban_words_set.remove(word)

        # 遍历敏感词，找到其在 DFA 字典中的路径
        for char in word:
            if char in now_dict:
                stack.append((char, now_dict))  # 记录当前字符和当前字典
                now_dict = now_dict[char]
            else:
                # 如果敏感词不存在，直接返回
                logger.warning(f"敏感词 '{word}' 不存在，无法删除")
                return False

        # 如果最后一个字符的 'is_end' 标志为 True，则删除敏感词
        if now_dict.get('is_end', False):
            now_dict['is_end'] = False  # 取消结束标志

            # 从后往前清理无效的节点
            while stack:
                char, parent_dict = stack.pop()
                if not now_dict:  # 如果当前字典为空
                    del parent_dict[char]  # 删除该字符节点
                elif len(now_dict) == 1 and 'is_end' in now_dict and not now_dict['is_end']:
                    del parent_dict[char]  # 删除无效的中间节点
                else:
                    break  # 如果当前节点仍有其他分支，则停止清理
                now_dict = parent_dict

            logger.info(f"敏感词 '{word}' 已成功删除")
            return True
        else:
            logger.warning(f"敏感词 '{word}' 不存在结束标志，无法删除")
            return False

    # 寻找第一次出现敏感词的位置
    def find_illegal(self, _str):
        now_dict = self.ban_words_dict
        i = 0
        start_word = -1
        is_start = True  # 判断是否是一个敏感词的开始
        while i < len(_str):
            if _str[i] not in now_dict:
                if is_start is True:
                    i += 1
                    continue
                i = start_word +1
                start_word = -1
                is_start = True
                now_dict = self.ban_words_dict
            else:
                if is_start is True:
                    start_word = i
                    is_start = False
                now_dict = now_dict[_str[i]]
                if now_dict['is_end'] is True:
                    return start_word
                else:
                    i += 1
        return -1

    # 查找是否存在敏感词
    def exists(self, s):
        pos = self.find_illegal(s)
        if pos == -1:
            return False
        else:
            return True

    # 将指定位置的敏感词替换为*
    def filter_words(self, filter_str, pos):
        now_dict = self.ban_words_dict
        end_str = int()
        for i in range(pos, len(filter_str)):
            if now_dict[filter_str[i]]['is_end'] is True:
                end_str = i
                break
            now_dict = now_dict[filter_str[i]]
        num = end_str - pos + 1
        filter_str = filter_str[:pos] + '*'*num + filter_str[end_str + 1:]
        return filter_str

    def filter_all(self, s):
        pos_list = list()
        ss = self.draw_words(s, pos_list)
        illegal_pos = self.find_illegal(ss)
        while illegal_pos != -1:
            ss = self.filter_words(ss, illegal_pos)
            illegal_pos = self.find_illegal(ss)
        i = 0
        while i < len(ss):
            if ss[i] == '*':
                start = pos_list[i]
                while i < len(ss) and ss[i] == '*':
                    i += 1
                i -=1
                end = pos_list[i]
                num = end-start+1
                s = s[:start] + '*'*num + s[end+1:]
            i += 1
        return s

    @staticmethod
    def draw_words(_str, pos_list):
        ss = str()
        for i in range(len(_str)):
            if '\u4e00' <= _str[i] <= '\u9fa5' or '\u3400' <= _str[i] <= '\u4db5' or '\u0030' <= _str[i] <= '\u0039' \
                    or '\u0061' <= _str[i] <= '\u007a' or '\u0041' <= _str[i] <= '\u005a':
                ss += _str[i]
                pos_list.append(i)
        return ss

dfa = DFA()
