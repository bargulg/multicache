import pickle
from time import time
from redis import Redis

from multicache.base import BaseCache


class RedisCache(BaseCache):
    def __init__(self, name='rediscache', **kwargs):
        self.name = name
        self.ttl = kwargs.pop('ttl', 3600)
        self.ex = self.ttl + time()
        self.redis = Redis()

    def get(self, key):
        redis_key = pickle.dumps(key)
        val = self.redis.get("{}:{}".format(self.name, redis_key))
        if val is not None:
            return pickle.loads(val)
        else:
            return None

    def put(self, key, value, ex=None, ttl=None):
        if ttl is None:
            if ex is not None:
                ttl = ex - time()
            else:
                ttl = self.ttl
        redis_key = pickle.dumps(key)
        redis_value = pickle.dumps(value)
        self.redis.set("{}:{}".format(self.name, redis_key), redis_value, ttl)

    def invalidate(self, key):
        self.redis.delete("{}:{}".format(self.name, pickle.dumps(key)))
