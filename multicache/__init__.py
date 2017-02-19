import hashlib
import os
import pickle
import tempfile
import zlib
from threading import Lock
from time import time

from multicache.base import BaseCache
try:
    from multicache.redis import RedisCache
except ImportError:
    pass

lock = Lock()


class DummyCache(BaseCache):
    """ Fake cache class to allow a "no cache"
        use without breaking anything """
    def __init__(self):
        self._dict = {}

    def get(self, key):
        return None

    def put(self, key, value, ex=None, ttl=None):
        pass

    def invalidate(self, key):
        pass


class DictCache(BaseCache):
    """ Saves data in a dictionary without any persistent storage """
    def __init__(self, **kwargs):
        self._dict = {}
        self.ttl = kwargs.pop('ttl', 3600)

    def get(self, key):
        ret = self._dict.get(key, None)
        if ret is not None and ret[1] > time():
            # cache hit
            return ret[0]
        elif ret is None:
            # cache miss
            return None
        else:
            # stale, delete from cache
            self.invalidate(key)
            return None

    def put(self, key, value, ex=None, ttl=None):
        with lock:
            if ex is None:
                if ttl is not None:
                    ex = ttl + time()
                else:
                    ex = self.ttl + time()
            self._dict[key] = value, ex

    def invalidate(self, key):
        self._dict.pop(key, None)

    def get_all_keys(self):
        return self._dict.keys()

    def get_all_values(self):
        return [val[0] for val in self._dict.values() if val[1] >= time()]

    def recheck(self):
        invalid = []
        for key, val in self._dict.items():
            if time() > val[1]:
                invalid.append(key)
        for key in invalid:
            self.invalidate(key)


class FileCache(BaseCache):
    """ Saves data to a dictionary and files, always saves to both,
    only reads files when data isn't in dictionary"""
    def __init__(self, path=None, **kwargs):
        self._cache = {}
        self.ttl = kwargs.pop('ttl', 3600)
        if path:
            self.path = path
        else:
            self.path = '{}/multicache'.format(tempfile.gettempdir())
        if not os.path.isdir(self.path):
            os.mkdir(self.path, 0o700)

    def _getpath(self, key):
        h = hashlib.new('md5')
        h.update(key.encode('utf-8'))
        return os.path.join(self.path, h.hexdigest() + '.cache')

    def put(self, key, value, ex=None, ttl=None):
        with lock:
            with open(self._getpath(key), 'wb') as f:
                if ex is None:
                    if ttl is not None:
                        ex = ttl + time()
                    else:
                        ex = self.ttl + time()
                f.write(zlib.compress(pickle.dumps((value, ex), -1)))
            self._cache[key] = (value, ex)

    def get(self, key):
        if key in self._cache:
            cached = self._cache[key]
            if cached[1] > time():
                return cached[0]

        try:
            with open(self._getpath(key), 'rb') as f:
                ret = pickle.loads(zlib.decompress(f.read()))
                if ret[1] > time():
                    # cache hit
                    return ret[0]

            # stale cache, invalidate
            self.invalidate(key)
            return None

        except IOError as ex:
            if ex.errno == 2:  # file does not exist (yet)
                return None
            else:
                raise

    def invalidate(self, key):
        with lock:
            self._cache.pop(key, None)

            try:
                os.unlink(self._getpath(key))
            except OSError as ex:
                if ex.errno == 2:  # does not exist
                    pass
                else:
                    raise
