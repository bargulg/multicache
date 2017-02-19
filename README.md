# Multicache

[![Build Status](https://travis-ci.org/bargulg/multicache.svg?branch=master)](https://travis-ci.org/bargulg/multicache)
[![Coverage Status](https://coveralls.io/repos/github/bargulg/multicache/badge.svg?branch=master)](https://coveralls.io/github/bargulg/multicache?branch=master)

Simple python caching mechanisms using expiration time or time to live.

Designed to be used with API clients and similar.

This module aims primarily to be simple and easy to use and extend.
It doesn't remove expired data unless you try to get it from cache.

## Installation

    pip install multicache

or

    git clone git@github.com:bargulg/multicache.git
    cd multicache
    python setup.py install

optionally for redis cache:

    pip install redis

## Usage
    
    from multicache import DictCache
    
    cache = DictCache()

    def search_with_cache(query='python'):
        headers = {'User-Agent': 'Mozilla/5.0'}
        request_url = 'https://duckduckgo.com'
        params = {'q': query}

        request_url = "{}?{}".format(url, urlencode(params))

        cached = cache.get(request_url)
        if cached:
            return cached
        else:
            req = Request(request_url, headers=headers)
            response = json.loads(urlopen(req).read().decode("utf-8"))
            cache.put(request_url, response)
            return response

## Types of cache

### RedisCache   (recommended)
Saves data in redis - fast, lightweight and reliable
Right now this supports only default redis settings, better support for redis
will come soon

### DictCache
Saves data in dict - this will be deleted when program is closed

### FileCache
Saves data in file as a persistent storage, good for long-term caching of small number of keys.
For speed, it also saves it in dict, and reads file whenever it doesn't find key in dict.

### DummyCache
Doesn't save anything, every call to get(key) is a cache miss 

### Your own custom, fancy cache
Just inherit from BaseCache and implement put(), get(), and invalidate()
