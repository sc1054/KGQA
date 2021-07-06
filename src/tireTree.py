#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/8 3:58 下午
# @Author  : sunchao


class TrieNode(object):
    def __init__(self):
        """初始化自己的数据结构"""
        self.data = {}
        self.is_word = False
        self.count = 0

        # TODO
        self.count_letter = 0  # 根节点为空


class Trie(object):
    """
    Trie的核心思想是空间换时间。利用字符串的公共前缀来降低查询时间的开销以达到提高效率的目的。
    它的插入和查询时间复杂度都为 O(n), n为树的高度（字符串的最大长度）
    应用：
        字符串检索 -> 事先将已知的一些字符串（字典）的有关信息保存到trie树里，查找另外一些未知字符串是否出现过或者出现频率。
        字符串最长公共前缀、排序、词频统计、字符串搜索的前缀匹配

        判断给定单词是否为trie树中单词（判断给定单词在trie树中出现过几次）
        trie树中某前缀的单词有多少个（有什么单词）
        查询一句话中的实体
    """
    def __init__(self):
        self.root = TrieNode()

    def add(self, word):
        node = self.root
        for letter in word:
            if letter not in node.data:  # 插入结点
                node.data[letter] = TrieNode()
            node = node.data[letter]  # 更新结点
            node.count_letter += 1
        node.is_word = True
        node.count += 1

    def isword(self, word) -> int:
        """判断给定单词在trie树中出现过几次"""
        node = self.root
        if not word:
            return 0
        for letter in word:
            node = node.data.get(letter, {})  # 不在字典树中返回0
            if not node:
                return 0
        return node.count if node.is_word else 0

    def num_startswith(self, prefix) -> int:
        """
        一种较快的方式返回trie中给定前缀的单词有多少个，不需要遍历所有单词
        只需要在数据结构中增加count_letter
        """
        node = self.root
        for letter in prefix:
            node = node.data.get(letter, {})
            if not node:
                return 0
        return node.count_letter

    def _get_key(self, prefix, pre_node) -> list:
        """返回前缀为prefix的所有词"""
        # print(pre_node.__dict__)
        word_list = []
        if pre_node.is_word:
            word_list.append(prefix)
        for x in pre_node.data.keys():
            word_list.extend(self._get_key(prefix + str(x), pre_node.data.get(x)))
        return word_list

    def get_startswith(self, prefix='') -> list:
        """
        返回给定前缀的单词
        当输入为prefix=''时，打印trie树中所有的词
        """
        node = self.root
        for letter in prefix:
            node = node.data.get(letter, {})  # 定位到最后一个letter
            if not node:
                return []
        return self._get_key(prefix, node)

    def find_entity(self, seq: str, longest=True, drop_duplicates=False) -> dict:
        """
        返回seq的实体及其位置
        :param seq: 话术
        :param longest: 嵌套实体情况下是否返回只返回最长的实体
        :return:

        eg: entity = e生保, e生保plus, e生保2020, 平安福
        --> find_entity(我想问一下e生保plus我想买e生保2020或者平安福符合条件吗)
        --> {(5, 11): 'e生保plus', (15, 21): 'e生保2020', (24, 26): '平安福'}
        --> {(5, 7): 'e生保', (5, 11): 'e生保plus', (15, 17): 'e生保', (15, 21): 'e生保2020', (24, 26): '平安福'}

        返回最长实体的区别在于什么时候判断传入的prefix是不是trie树中的词
        """
        res, prefix = {}, ""
        for i, letter in enumerate(seq):
            if self.num_startswith(prefix + letter):  # 存在以prefix+letter为前缀的词
                prefix += letter
                if self.isword(prefix):
                    res[(i - len(prefix) + 1, i)] = prefix
            else:
                prefix = letter

        if len(res) == 1:
            return res

        # 取出重叠实体
        if longest:
            res = dict(sorted(res.items(), key=lambda x: x[0][1], reverse=True))
            res = dict(sorted(res.items(), key=lambda x: x[0][0], reverse=False))

            # 如果key中第一个index一样，则有长实体嵌套短实体的现象
            pre = ()
            keep_keys = []
            for key in res:
                keep_keys.append(key)
                if not pre:
                    pre = key
                    continue
                if key[0] == pre[0] and key[1] < pre[1]:
                    keep_keys.pop()
                pre = key
            res = {key: res[key] for key in keep_keys}

        # 实体去重
        if drop_duplicates:
            def rdictf(ff_dict):
                return dict([(x, y) for y, x in ff_dict.items()])

            res = rdictf(rdictf(res))

        return res

    def find_fuzzy_entity(self, seq) -> dict:
        """基于编辑距离相似度的模糊实体查询"""
        pass

    def find_entity_v0(self, context) -> dict:
        """
        找到context中的实体及其位置，嵌套实体只返回较长的实体

        eg: entity = e生保, e生保plus, e生保2020
        --> find_entity(我想问一下e生保plus我想买e生保2020或者平安福符合条件吗)
        --> {(5, 11): 'e生保plus', (15, 21): 'e生保2020'}

        """
        res, prefix, count = {}, "", 0
        for i, word in enumerate(context):
            # prefix动态变化
            if self.num_startswith(prefix + word):
                count += len(word)
                prefix += word
                print(prefix)
            elif self.isword(prefix):  # 确定找到实体，确定实体的index
                res[(count - len(prefix), count - 1)] = prefix
                prefix = word if self.num_startswith(word) else ""
                count += len(word)
            else:  # 还未找到实体，继续寻找
                count += len(word)
                prefix = word if self.num_startswith(word) else ""
        if self.isword(prefix):
            res[(count - len(prefix), count - 1)] = prefix
        return res

    # TODO
    def __str__(self):
        pass

    def print_tree(self, tree):
        buff = ['Root/']
        self._print_tree(tree.__dict__['root'].__dict__, buff, '', 0)
        print('\n'.join(buff))

    def _print_tree(self, tree: dict, buff, prefix, level):
        count = len(tree)
        for k, v in tree['data'].items():
            count -= 1
            if v:
                buff.append('%s->%s/' % (prefix, k))
                if count > 0:
                    self._print_tree(v.__dict__, buff, prefix + '|', level + 1)
                else:
                    self._print_tree(v.__dict__, buff, prefix + '', level + 1)
            else:
                buff.append('%s+-%s' % (prefix, k))


if __name__ == '__main__':
    trie = Trie()
    trie.add('ee生保')
    trie.add('e生保plus')
    trie.add('e生保2020')
    trie.add('e生保2021')
    trie.add('平安福')
    trie.add('e生保')
    trie.add('非典')
    trie.add('感冒')
    # print(Trie.__dict__)
    # print(trie.__dict__)
    # print(trie.print_tree(trie))
    print(trie.num_startswith('e生'))
    print(trie.get_startswith(''))
    print(trie.isword('e生保'))
    print(trie.find_entity('e生保2021我想问一下e生保plus我想买e生保2020或者平安福符合条件吗'))
    print(trie.find_entity('e生保2021我想问一下e生保plus我想买e生保2020或者平安福符合条件吗', longest=False, drop_duplicates=True))
    print(trie.find_entity('e生保2021我想问一下e生保plus我想买e生保2020或者平安福符合条件吗', longest=False, drop_duplicates=False))
    print(trie.find_entity('非典感冒', longest=False))
    print(trie.find_entity('非典感冒', longest=True))

    # import re
    # re.search()
