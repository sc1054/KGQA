#!/usr/bin/env python3
# coding: utf-8

import os
import ahocorasick

from src.redis_helper import RedisHelper
from src.tireTree import Trie
import copy


class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # redis
        self.prefix = 'kg_'
        self.redis = RedisHelper()
        # 　特征词路径
        self.disease_path = os.path.join(cur_dir, 'dict/disease.txt')
        self.department_path = os.path.join(cur_dir, 'dict/department.txt')
        self.check_path = os.path.join(cur_dir, 'dict/check.txt')
        self.drug_path = os.path.join(cur_dir, 'dict/drug.txt')
        self.food_path = os.path.join(cur_dir, 'dict/food.txt')
        self.producer_path = os.path.join(cur_dir, 'dict/producer.txt')
        self.symptom_path = os.path.join(cur_dir, 'dict/symptom.txt')
        self.deny_path = os.path.join(cur_dir, 'dict/deny.txt')
        # 加载特征词，根据特征词确定实体
        # 目前有疾病、科室、药品、实物、并发症、诊断检查项目、在售药品
        self.disease_wds = [i.strip() for i in open(self.disease_path) if i.strip()]
        self.department_wds = [i.strip() for i in open(self.department_path) if i.strip()]
        self.check_wds = [i.strip() for i in open(self.check_path) if i.strip()]
        self.drug_wds = [i.strip() for i in open(self.drug_path) if i.strip()]
        self.food_wds = [i.strip() for i in open(self.food_path) if i.strip()]
        self.producer_wds = [i.strip() for i in open(self.producer_path) if i.strip()]
        self.symptom_wds = [i.strip() for i in open(self.symptom_path) if i.strip()]
        self.region_words = set(
            self.department_wds + self.disease_wds + self.check_wds + self.drug_wds + self.food_wds + self.producer_wds + self.symptom_wds)
        self.deny_words = [i.strip() for i in open(self.deny_path) if i.strip()]
        # 构建字典树
        self.region_tree = Trie()
        for word in list(self.region_words):
            self.region_tree.add(word)
        # self.region_tree = self.build_actree(list(self.region_words))

        # 构建词典  词：类型
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词
        self.symptom_qwds = ['症状', '表征', '现象', '症候', '表现']
        self.cause_qwds = ['原因', '成因', '为什么', '怎么会', '怎样才', '咋样才', '怎样会', '如何会', '为啥', '为何', '如何才会', '怎么才会', '会导致',
                           '会造成']
        self.acompany_qwds = ['并发症', '并发', '一起发生', '一并发生', '一起出现', '一并出现', '一同发生', '一同出现', '伴随发生', '伴随', '共现']
        self.food_qwds = ['饮食', '饮用', '吃', '食', '伙食', '膳食', '喝', '菜', '忌口', '补品', '保健品', '食谱', '菜谱', '食用', '食物', '补品']
        self.drug_qwds = ['药', '药品', '用药', '胶囊', '口服液', '炎片']
        self.prevent_qwds = ['预防', '防范', '抵制', '抵御', '防止', '躲避', '逃避', '避开', '免得', '逃开', '避开', '避掉', '躲开', '躲掉', '绕开',
                             '怎样才能不', '怎么才能不', '咋样才能不', '咋才能不', '如何才能不',
                             '怎样才不', '怎么才不', '咋样才不', '咋才不', '如何才不',
                             '怎样才可以不', '怎么才可以不', '咋样才可以不', '咋才可以不', '如何可以不',
                             '怎样才可不', '怎么才可不', '咋样才可不', '咋才可不', '如何可不']
        self.lasttime_qwds = ['周期', '多久', '多长时间', '多少时间', '几天', '几年', '多少天', '多少小时', '几个小时', '多少年']
        self.cureway_qwds = ['怎么治疗', '如何医治', '怎么医治', '怎么治', '怎么医', '如何治', '医治方式', '疗法', '咋治', '怎么办', '咋办', '咋治']
        self.cureprob_qwds = ['多大概率能治好', '多大几率能治好', '治好希望大么', '几率', '几成', '比例', '可能性', '能治', '可治', '可以治', '可以医']
        self.easyget_qwds = ['易感人群', '容易感染', '易发人群', '什么人', '哪些人', '感染', '染上', '得上']
        self.check_qwds = ['检查', '检查项目', '查出', '检查', '测出', '试出']
        self.belong_qwds = ['属于什么科', '属于', '什么科', '科室']
        self.cure_qwds = ['治疗什么', '治啥', '治疗啥', '医治啥', '治愈啥', '主治啥', '主治什么', '有什么用', '有何用', '用处', '用途',
                          '有什么好处', '有什么益处', '有何益处', '用来', '用来做啥', '用来作甚', '需要', '要']

        print('model init finished ......')

        return

    def judge_qes(self, question, types, ls_state):
        # TODO 问答类型这一部分可以用flashtext加快查找速度
        question_types = []
        question_type = 'others'

        # 症状
        if self.check_words(self.symptom_qwds, question) and ('disease' in types):
            question_type = 'disease_symptom'
            question_types.append(question_type)

        # 症状可能的疾病
        if self.check_words(self.symptom_qwds, question) and ('symptom' in types):
            question_type = 'symptom_disease'
            question_types.append(question_type)
        # 原因
        if self.check_words(self.cause_qwds, question) and ('disease' in types):
            question_type = 'disease_cause'
            question_types.append(question_type)
        # 并发症
        if self.check_words(self.acompany_qwds, question) and ('disease' in types):
            question_type = 'disease_acompany'
            question_types.append(question_type)
        # 推荐食品（某种疾病可以吃，不能吃）
        if self.check_words(self.food_qwds, question) and 'disease' in types:
            deny_status = self.check_words(self.deny_words, question)
            if deny_status:
                question_type = 'disease_not_food'
            else:
                question_type = 'disease_do_food'
            question_types.append(question_type)
        # 已知食物找疾病（哪些人最好（不）吃某种food）
        if self.check_words(self.food_qwds + self.cure_qwds, question) and 'food' in types:
            deny_status = self.check_words(self.deny_words, question)
            if deny_status:
                question_type = 'food_not_disease'
            else:
                question_type = 'food_do_disease'
            question_types.append(question_type)
        # 推荐药品（啥病要吃啥药）
        if self.check_words(self.drug_qwds, question) and 'disease' in types:
            question_type = 'disease_drug'
            question_types.append(question_type)
        # 药品治啥病（啥药可以治啥病）
        if self.check_words(self.cure_qwds, question) and 'drug' in types:
            question_type = 'drug_disease'
            question_types.append(question_type)
        # 疾病接受检查项目
        if self.check_words(self.check_qwds, question) and 'disease' in types:
            question_type = 'disease_check'
            question_types.append(question_type)
        # 已知检查项目查相应疾病
        if self.check_words(self.check_qwds + self.cure_qwds, question) and 'check' in types:
            question_type = 'check_disease'
            question_types.append(question_type)
        # 　症状防御
        if self.check_words(self.prevent_qwds, question) and 'disease' in types:
            question_type = 'disease_prevent'
            question_types.append(question_type)
        # 疾病医疗周期
        if self.check_words(self.lasttime_qwds, question) and 'disease' in types:
            question_type = 'disease_lasttime'
            question_types.append(question_type)
        # 疾病治疗方式
        if self.check_words(self.cureway_qwds, question) and 'disease' in types:
            question_type = 'disease_cureway'
            question_types.append(question_type)
        # 疾病治愈可能性
        if self.check_words(self.cureprob_qwds, question) and 'disease' in types:
            question_type = 'disease_cureprob'
            question_types.append(question_type)
        # 疾病易感染人群
        if self.check_words(self.easyget_qwds, question) and 'disease' in types:
            question_type = 'disease_easyget'
            question_types.append(question_type)

        # 没有查询到问句信息，从上一轮中拉取
        if not question_types:
            question_types = ls_state['question_types']
        # 若没有查到相关的外部查询信息，那么则将该疾病的描述信息返回
        if question_types == [] and 'disease' in types:
            question_types = ['disease_desc']
        # 若没有查到相关的外部查询信息，那么则将该疾病的描述信息返回
        if question_types == [] and 'symptom' in types:
            question_types = ['symptom_disease']

        return question_types

    def classify(self, question, user_id):
        """
        分类主函数
        传入用户问题、redis类、用户id
        逻辑为先判断询问实体，然后判断问答类型
        """
        ls_state = self.redis.key_get(self.prefix + user_id)
        cur_state = copy.deepcopy(ls_state)

        # --1-- 提取实体信息
        # 若提取到了实体则用当前实体，并覆盖掉之前的实体，若没有从redis中拉取上一轮的实体信息
        # medical_dict = self.check_medical(question)
        medical_dict = self.check_entity(question)
        print(medical_dict)
        if not medical_dict:
            if not ls_state['args']:  # 实体缺失
                # TODO 实体缺失发起询问
                pass
            else:
                medical_dict = ls_state['args']
        else:  # 提取到了实体，更新当前状态
            cur_state['args'] = medical_dict

        # 收集问句当中所涉及到的实体类型
        types = [type_[0] for type_ in medical_dict.values()]

        # --2-- 基于特征词判断问答类型，支持18种问答
        cur_state['question_types'] = self.judge_qes(question, types, ls_state)

        # 更新状态
        self.redis.key_insert(self.prefix + user_id, cur_state)

        # TODO 如果ls_state == cur_state默认为用户当前句并没有提及到任何有用的信息
        # if ls_state == cur_state:
        #     return {}
        return cur_state

    def build_wdtype_dict(self):
        """构造词对应的类型"""
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.disease_wds:
                wd_dict[wd].append('disease')
            if wd in self.department_wds:
                wd_dict[wd].append('department')
            if wd in self.check_wds:
                wd_dict[wd].append('check')
            if wd in self.drug_wds:
                wd_dict[wd].append('drug')
            if wd in self.food_wds:
                wd_dict[wd].append('food')
            if wd in self.symptom_wds:
                wd_dict[wd].append('symptom')
            if wd in self.producer_wds:
                wd_dict[wd].append('producer')
        return wd_dict

    def build_actree(self, wordlist):
        """构造actree，加速过滤"""
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    def check_medical(self, question):
        """问句过滤"""
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}

        return final_dict

    def check_entity(self, question):
        entity = self.region_tree.find_entity(str(question), longest=True, drop_duplicates=True)
        final_dict = {item: self.wdtype_dict.get(item) for item in entity.values()}
        return final_dict

    def check_words(self, wds, sent):
        """基于特征词进行分类"""
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    """
        sent:豆仁饭感冒可以吃吗
        res_classify: {'args': {'豆仁饭': ['food'], '感冒': ['disease']}, 
                        'question_types': ['disease_do_food', 'food_do_disease']}
    """
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question, user_id='0000')
        print(data)
