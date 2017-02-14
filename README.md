# SimpleCache
Simple python caching mechanisms.
This module aims primarily to be simple and easy to use and extend.
It doesn't remove expired data unless you try to get it from cache.

## Usage
    
    from simple_cache import DictCache
    
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
