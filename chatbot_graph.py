#!/usr/bin/env python3
# coding: utf-8

from question_classifier import QuestionClassifier
from question_parser import QuestionPaser
from answer_search import AnswerSearcher

from src.redis_helper import RedisHelper


class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

        self.redis = RedisHelper()
        self.redis.redis_restart()

        self.prefix = 'kg_'

    def chat_main(self, sent, user_id='000'):
        answer = '您好，我是智能医药智能助理，希望可以帮到您。如果没答上来，可联系*****。祝您身体棒棒！'
        # restart即为重启
        if sent == 'restart':
            self.redis.redis_restart()
            return answer
        # 先到redis中拉取历史对话信息
        res_classify = self.classifier.classify(sent, user_id)
        """
        sent:豆仁饭感冒可以吃吗
        res_classify: {'args': {'豆仁饭': ['food'], '感冒': ['disease']}, 
                        'question_types': ['disease_do_food', 'food_do_disease']}
        """
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)


if __name__ == '__main__':
    bot = ChatBotGraph()
    while 1:
        question = input('用户:')
        answer = bot.chat_main(question, user_id='000')
        print('机器人:', answer)
