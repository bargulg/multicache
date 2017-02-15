from multicache import DictCache, FileCache, DummyCache
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
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(8)])


@pytest.fixture(scope='function', params=[DictCache, FileCache])
def cache(request):
    return request.param()


def test_empty_cache(cache, random_key):
    assert cache.get(random_key) is None


def test_cache(cache, random_key, random_value):
    cache.put(random_key, random_value)
    assert cache.get(random_key) == random_value


def test_invalidate(cache, random_key, random_value):
    cache.put(random_key, random_value)
    cache.invalidate(random_key)
    assert cache.get(random_key) is None


def test_invalidate_nonexistent(cache, random_key):
    cache.invalidate(random_key)


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
