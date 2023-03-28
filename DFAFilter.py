# 屏蔽词：新疆骚乱、爆炸、骚乱,新疆爆炸
# 生成一个类似树状图的字典结构
# ‘’: {‘疆’: {‘骚’: {‘乱’: {’\x00’: 0}}}}
# ‘爆’: {‘炸’: {’\x00’: 0}}
# ‘骚’: {‘乱’: {’\x00’: 0}}
# keyword_chains = {‘新’: {‘疆’: {‘骚’: {‘乱’: {’\x00’: 0}}}, ‘爆’: {‘炸’: {’\x00’: 0}}}},
#                   ‘爆’: {‘炸’: {’\x00’: 0}},
#                   ‘骚’: {‘乱’: {’\x00’: 0}}}

import time

time1 = time.time()


class DFAFilter(object):
    def __init__(self):
        self.keyword_chains = {}  # 屏蔽词链表
        self.delimit = '\x00'  # \x00是空字符，每个屏蔽词的结尾都加上表示匹配到整词结束

    # 处理文本，切分每个屏蔽词，分别加入链中
    def parseSensitiveWords(self, path):
        with open(r'shieldwords.txt', encoding='UTF-8') as f:
            WordList = f.read().split(',')
            for keyword in WordList:
                self.add_Chains(keyword.strip())

    # 将屏蔽词表加入词典树状结构中
    def add_Chains(self, keyword):
        keyword = keyword.lower()  # 变小写
        chars = keyword.strip()  # 去除首位空格和换行
        if not chars:  # 关键词为空直接返回
            return
        level = self.keyword_chains
        # 遍历关键字的每个字
        for i in range(len(chars)):
            # 如果这个字符已经存在key,就进入其子字典,迭代到最后的子字典为空字典
            if chars[i] in level:
                level = level[chars[i]]
            else:  # 进入了一个空字典
                if not isinstance(level, dict):  # 如果不是字典类型，即进入到没有子字典的key，即遇到重复屏蔽词
                    break
                # 开始嵌套字典
                for j in range(i, len(chars)):
                    level[chars[j]] = {}  # ··{·· {} 变为 ·{··{'chars[j]': {}}

                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]  # level引用变为 {'chars[j]': {}} 中的{}
                last_level[last_char] = {self.delimit: 0}  # 屏蔽词结尾后加个\x00  {'x': {\x00: 0 }}
                break  # for j完成后结束for i循环
        if i == len(chars) - 1:  # 对于字典已有abcde，然后这次加入‘abc’的情况
            level[self.delimit] = 0

    def filter(self, message, repl):  # 用*替代屏蔽字
        message = message.lower()
        start = 0
        rep = []  # 列表存放替换后的句子
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        if start == len(message) - 1:  # 要是剩下最后一个字的话，进入了(if char in level:)之后就不会append了
                            rep.append(message[start])
                        else:
                            level = level[char]
                    else:
                        rep.append(repl * step_ins)
                        start += step_ins - 1  # -1是因为外循环结束的时候统一+1
                        break  # 屏蔽了一个词句(step_ins个字符)，跳出以start开始遍历字串的循环，进入下一个statr
                else:
                    rep.append(message[start])
                    break  # 该start没有在字典中，进入下一个start

            start += 1
        return ''.join(rep)


if __name__ == '__main__':
    dfa = DFAFilter()
    dfa.parseSensitiveWords('shieldwords.txt')
    print(dfa.filter("小明点为什么解", "*"))
    time2 = time.time()
    print('总耗时：' + str(time2 - time1) + 's')

# 问题：程序在处理 (屏蔽词典：abcd abcde)  print(abcde) → ****e 而非 *****
