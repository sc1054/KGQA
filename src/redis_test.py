#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/1 3:10 下午
# @Author  : sunchao

from redis_helper import RedisHelper

r = RedisHelper()
info = r.key_get('kg_00')
print(info['args'])
print()
