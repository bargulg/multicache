from time import time
import os
import zlib
import hashlib

import pickle
import tempfile


class APICache(object):
    """
    Every cache should be a subclass of this class
    """
    def put(self, key, value, ex=None, ttl=None):
        """
        Put a new value for key in cache
        :param key: key (usually URL of resource)
        :param value: value (usually text of response)
        :param ex: expiry time (unix time)
        :param ttl: how long should Item be cached (seconds)
        """
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def invalidate(self, key):
        raise NotImplementedError


class DummyCache(APICache):
    """ Fake cache class to allow a "no cache"
        use without anything """
    def __init__(self):
        self._dict = {}

    def get(self, key):
        return None

    def put(self, key, value, ex=None, ttl=None):
        pass

    def invalidate(self, key):
        pass


class DictCache(APICache):
    """ Saves data in a dictionary without any persistent storage """
    def __init__(self, **kwargs):
        self._dict = {}
        self.ex = kwargs.pop('ex', 3600)

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
        if ex is None:
            if ttl is not None:
                ex = ttl + time()
            else:
                ex = self.ex
        self._dict[key] = value, ex + time()

    def invalidate(self, key):
        self._dict.pop(key, None)

    def get_all_keys(self):
        return self._dict.keys()

    def get_all_values(self):
        return self._dict.values()

    def recheck(self):
        for key, val in self._dict.items():
            if time() > val(1):
                self.invalidate(key)


class FileCache(APICache):
    def __init__(self, path=None, **kwargs):
        self._cache = {}
        self.ex = kwargs.pop('ex', 3600)
        if path:
            self.path = path
        else:
            self.path = '{}/mtgsdk'.format(tempfile.gettempdir())
        if not os.path.isdir(self.path):
            os.mkdir(self.path, 0o700)

    def _getpath(self, key):
        h = hashlib.new('md5')
        h.update(key.encode('utf-8'))
        return os.path.join(self.path, h.hexdigest() + '.cache')

    def put(self, key, value, ex=None, ttl=None):
        with open(self._getpath(key), 'wb') as f:
            if ex is None:
                ex = self.ex
            f.write(zlib.compress(pickle.dumps((value, ex + time()), -1)))
        self._cache[key] = value

    def get(self, key):
        if key in self._cache:
            return self._cache[key]

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
        self._cache.pop(key, None)

        try:
            os.unlink(self._getpath(key))
        except OSError as ex:
            if ex.errno == 2:  # does not exist
                pass
            else:
                raise