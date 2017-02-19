class BaseCache(object):
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
