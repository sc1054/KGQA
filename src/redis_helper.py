# 向后兼容，建议使用StrictRedis
from redis import Redis, StrictRedis
from multiprocessing import Pool
import json

# 操作集群
# from rediscluster import StrictRedis


class RedisHelper(object):
    def __init__(self):
        self.r = StrictRedis(host='localhost', port=6379, db=0, password='test')
        self.default_value = {'args': {}, 'question_types': []}

        # 区别redis中所有的key
        self.prefix = 'kg_'

    def del_keys(self, keys):
        for key in keys:
            self.r.delete(key)

    def del_all(self, use_async=False):
        """遍历所有的前缀为prefix的key并删除"""
        key_list = list(self.r.scan_iter(match=self.prefix + '*', count=10000))
        if not use_async:
            self.del_keys(key_list)
        else:
            p = Pool(processes=4)
            batch_keys = 1000
            keys = [key_list[i:i+batch_keys] for i in range(0, len(key_list), batch_keys)]
            for key in keys:
                p.apply_async(self.del_keys, args=(key,))
            p.close()
            p.join()

    def is_exits(self, key):
        """0 or 1"""
        return True if self.r.exists(key) else False

    def expire_set(self, key, value, time=60):
        """true or false"""
        res = self.r.set(key, value)
        if res:
            self.r.expire(key, time=time)   # 有效时间60s
        return res

    def key_insert(self, key, value):
        value = json.dumps(value)
        res = self.r.set(key, value)
        # 设置过期时间 60s
        self.r.expire(key, time=60)
        return res

    def key_get(self, key):
        if not self.is_exits(key):
            self.key_insert(key, self.default_value)
        res = self.r.get(key)
        res = json.loads(res)
        return res

    def redis_restart(self):
        self.del_all()


if __name__ == '__main__':
    redis_helper = RedisHelper()
    print(redis_helper.expire_set('test', 'test_value'))
    print(redis_helper.is_exits('test'))




