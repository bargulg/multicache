from time import sleep, time

from multicache import DictCache, FileCache, DummyCache, BaseCache, RedisCache
import pytest
import string
import random


@pytest.fixture(scope='function')
def random_key():
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(8)])


@pytest.fixture(scope='function')
def random_value():
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(8)])


@pytest.fixture(scope='function')
def random_path():
    return '.' +\
           ''.join([random.choice(string.ascii_lowercase) for _ in range(8)])


@pytest.fixture(scope='function', params=[DictCache, FileCache, RedisCache])
def cache(request):
    return request.param(ttl=2)


def test_crud(cache, random_key, random_value):
    assert cache.get(random_key) is None
    cache.invalidate(random_key)
    cache.put(random_key, random_value)
    assert cache.get(random_key) == random_value
    cache.put(random_key + '_', random_value + '_')
    assert cache.get(random_key + '_') == random_value + '_'
    cache.put(random_key, random_value + '_')
    assert cache.get(random_key) == random_value + '_'
    cache.invalidate(random_key)
    assert cache.get(random_key) is None


def test_dummy_cache(random_key, random_value):
    cache = DummyCache()
    assert cache.get(random_key) is None
    cache.put(random_key, random_value)
    assert cache.get(random_key) is None
    cache.invalidate(random_key)


def test_file_cache(random_key, random_value):
    cache = FileCache()
    cache.put(random_key, random_value)
    cache = FileCache()
    assert cache.get(random_key) == random_value


def test_file_cache_random_path(random_key, random_value, random_path):
    cache = FileCache(path=random_path)
    cache = FileCache()
    cache.put(random_key, random_value)
    assert cache.get(random_key) == random_value
    cache = FileCache()
    assert cache.get(random_key) == random_value


def test_listable_cache(random_key, random_value):
    cache = DictCache()
    for i in range(5):
        cache.put(random_key + str(i), random_value + str(i))
    assert random_key + '3' in cache.get_all_keys()
    assert random_value + '3' in cache.get_all_values()
    cache.recheck()


def test_recheck_expired(random_key, random_value):
    cache = DictCache(ttl=2)
    for i in range(5):
        cache.put(random_key + str(i), random_value + str(i))
    sleep(3)
    cache.recheck()
    assert cache.get(random_key + '2') is None


def test_expiration(cache, random_key, random_value):
    cache.put(random_key, random_value)
    assert cache.get(random_key) == random_value
    sleep(3)
    assert cache.get(random_key) is None
    cache.put(random_key, random_value, ttl=5)
    sleep(3)
    assert cache.get(random_key) == random_value
    sleep(3)
    assert cache.get(random_key) is None
    cache.put(random_key, random_value, ex=time() + 5)
    sleep(3)
    assert cache.get(random_key) == random_value
    sleep(3)
    assert cache.get(random_key) is None


def test_base_cache():
    # this is the only test that's there just for coverage
    # no other way to test BaseCache is needed
    cache = BaseCache()
    try:
        cache.get(None)
    except NotImplementedError:
        pass
    try:
        cache.put(None, None)
    except NotImplementedError:
        pass
    try:
        cache.invalidate(None)
    except NotImplementedError:
        pass
