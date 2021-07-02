#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/1 4:36 下午
# @Author  : sunchao

import os
import logging
from datetime import datetime


def record_log(msg, log_dir='/'.join(os.path.abspath(__file__).split('/')[:-1])):
    date = str(datetime.now()).split()[0]
    log_file_name = 'kg_chatbot_{}.log'.format(date)
    log_name = log_file_name.split('.')[0]
    logger = logging.getLogger(log_name)
    log_dir = os.path.join(log_dir, 'kg_bot')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_file = os.path.join(log_dir, log_file_name)
    handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = logging.Formatter('%(levelname)s-%(asctime)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info(msg)
    logger.removeHandler(handler)
