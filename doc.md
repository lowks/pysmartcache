# Table of contents:

1. [Basic usage](#basic-usage)
  1. [Installation](#installation)
  2. [Simplest case](#simplest-case)
  3. [Keys inclusion/exclusion](#keys-inclusionexclusion)
  4. [Defining keys in-depth](#defining-keys-in-depth)
  5. [Defining cache uniqueness](#defining-cache-uniqueness)
2. [Cache helpers](#cache-helpers)
  1. [Get info about a cache](#get-info-about-a-cache)
  2. [Invalidate cache](#invalidate-cache)
  3. [Refresh cache](#refresh-cache)
3. [Extra settings](#extra-settings)
  1. [Cache backend](#cache-backend)
  2. [Cache Time to live / timeout](#cache-time-to-live--timeout)
  3. [Cache host](#cache-host)
  4. [Cache verbosity](#cache-verbosity)
4. [Advanced usage](#advanced-usage)
  1. [Defining a custom connection to the client](#defining-a-custom-connection-to-the-client)
  2. [Defining your own clients](#defining-your-own-clients)
  3. [Creating custom unique representation rules](#creating-custom-unique-representation-rules)
5. [Contributing](#contributing)
  1. [Preparing environment](#preparing-environment)
  2. [Rules to contribute](#rules-to-contribute)


## Basic usage

### Installation
This lib can use as backend [memcached](http://memcached.org/) or [redis](http://redis.io/). Please install the one you want to use first.     
After this, you just need to run `pip install pysmartcache`.

### Simplest case
Let's suppose you have a heavy function and you want to cache it. Of course you can deal with cache manually... or, you can just use the `@cache()` decorator.   
`@cache()` by default will cache this function according to its parameters - just like the `memoizer` design pattern. So the simplest usage case is:
```python
from pysmartcache import cache


@cache()
def calculate_universe_mass(some_parameter, another_parameter, whatever):
    return 42
```

### Keys inclusion/exclusion
Now let's suppose you have a heavy function that receives a parameter such `verbose=True`. Well, (hopefully) this parameter will not change the result of function execution itself, so `@cache()` should ignore it.  
For this to work you can use `include` or `exclude` parameters.  
Using include:
```python
from pysmartcache import cache


@cache(include=['some_parameter', 'another_parameter', 'whatever'])
def calculate_universe_mass(some_parameter, another_parameter, whatever, verbose=True):
    return 42
```

OR using exclude:
```python
from pysmartcache import cache


@cache(exclude=['verbose'])
def calculate_universe_mass(some_parameter, another_parameter, whatever, verbose=True):
    return 42
```

### Defining keys in-depth
Sometimes you are trying to cache a method which `self` is not such a good key for cache itself.  
Let's suppose you have a class `Statistics`, related to an `Investor`, which has an identifier `uuid` attribute. Using `@cache()` as-is will try to cache based on `self`, when we wanted to cache based on `self.investor.uuid`. Voila:
```python
from pysmartcache import cache


class Investor(object):
    def __init__(self, uuid):
        self.uuid = uuid


class Statistics(object):
    def __init__(self, investor):
        self.investor = investor

    @cache(include=['self.investor.uuid', ])
    def get_internal_return_rate(self):
        return 42
```

### Defining cache uniqueness
On example below: what if we had 100 methods inside `Statistics` class? Would we need define the cache key as being `['self.investor.uuid', ]` every single time? No, we wouldn't.  
`pysmartcache` has a lookup for finding the unique representation of every attribute used as a cache key. You can define this attribute manually by creating a method `__cache_key__(self)` inside your classes. Note that this method must return a string. So the example below could be rewritten as follows:
```python
from pysmartcache import cache


class Investor(object):
    def __init__(self, uuid):
        self.uuid = uuid


class Statistics(object):
    def __init__(self, investor):
        self.investor = investor

    def __cache_key__(self):
        return str(self.investor.uuid)

    @cache()
    def get_internal_return_rate(self):
        return 42
```


## Cache helpers
`pysmartcache` monkeypatches some functions to you `@cache` decorated functions/methods. They are useful for cache management.

### Get info about a cache
In order to get info regarding a cache, use the following:
```python
from pysmartcache import cache


@cache()
def its_a_sum(a, b):
    return a + b


its_a_sum.cache_info_for(2, 3)
# will return None, which means that this value is not cached

assert its_a_sum(2, 3) == 5

its_a_sum.cache_info_for(2, 3)
# {'age': 0.000508,
#  'date added': datetime.datetime(2015, 12, 17, 23, 37, 47, 891876),
#  'outdated': False,
#  'timeout': 3600,
#  'value': 5}
```

### Invalidate cache
In order to clean a cache, use the following:
```python
from pysmartcache import cache


@cache()
def its_a_sum(a, b):
    return a + b


assert its_a_sum(2, 4) == 6

its_a_sum.cache_info_for(2, 4)
# some stuff here, cache found

its_a_sum.cache_invalidate_for(2, 4)

its_a_sum.cache_info_for(2, 4)
# will return None, which means that this value is not cached
```

### Refresh cache
Refreshing a cache will force cached function's re-execution and update its time to live:
```python
import time

from pysmartcache import cache


@cache()
def its_a_sum(a, b):
    return a + b


assert its_a_sum(2, 4) == 6

time.sleep(5)
its_a_sum.cache_info_for(2, 4)
# {'age': 5.1000, ...

its_a_sum.cache_refresh_for(2, 4)

its_a_sum.cache_info_for(2, 4)
# {'age': 0.0001, ...  <- cache was just re-created
```


## Extra settings

### Cache backend
Default cache backend is `memcached`. For now `memcached` and `redis` are supported. You can use redis by:
- Changing `cache_backend` parameter on `@cache()` call;
- Setting `PySmartCacheSettings.cache_backend` on your project entry-point;
- Defining an environment var called `PYSMARTCACHE_BACKEND`.  

Note that decorator call parameter supersedes `PySmartCacheSettings.cache_backend`, which superedes OS var, which obviously supersedes the default value.

### Cache Time to live / timeout
Default cache time to live / timeout is `3600` seconds (a.k.a. 1 hour). You can change it by:
- Using `timeout` parameter on `@cache()` call;
- Setting `PySmartCacheSettings.timeout` on your project entry-point;
- Defining an environment var called `PYSMARTCACHE_TIMEOUT`.  

Note that you must define a positive and integer value.  
Note that decorator call parameter supersedes `PySmartCacheSettings.cache_backend`, which superedes OS var, which obviously supersedes the default value.

### Cache host
Default hosts is `['127.0.0.1:11211', ]` for `memcached` and `'127.0.0.1:6379'` for `redis`. You can change it by:
- Using `cache_host` parameter on `@cache()` call;
- Setting `PySmartCacheSettings.cache_host` on your project entry-point;
- Defining an environment var called `PYSMARTCACHE_HOST`.  

Note that decorator call parameter supersedes `PySmartCacheSettings.cache_backend`, which superedes OS var, which obviously supersedes the default value.

### Cache verbosity
Default verbose parameter is `False`. It's useful to change it when you need to debug cache behavior, and so on. You can change it by:
- Using `verbose` parameter on `@cache()` call;
- Setting `PySmartCacheSettings.verbose` on your project entry-point;
- Defining an environment var called `PYSMARTCACHE_VERBOSE`.  

Note that `PYSMARTCACHE_VERBOSE` can only assume values `0` (which is `False`) and `1` (which is `True`).  
Note that decorator call parameter supersedes `PySmartCacheSettings.cache_backend`, which superedes OS var, which obviously supersedes the default value.


## Advanced usage

### Defining a custom connection to the client
`PySmartCache` comes with `memcached` and `redis` clients implemented. Client connection itself can be customized (in order to pass credentials, set behaviors, and so on).  
All you have to do is define `PySmartCacheSettings.cache_client` on your project entry-point.  
Take a look at this example:
```python
import pylibmc

from pysmartcache import PySmartCacheSettings


PySmartCacheSettings.cache_client = pylibmc.Client(['127.0.0.1:11211', ], username='admin', password='sikret',
                                                   behaviors={'tcp_nodelay': True, 'ketama': True})
```
You can even use a callable. See below:
```python
import pylibmc

from pysmartcache import PySmartCacheSettings


def gimme_the_client():
    return pylibmc.Client(['127.0.0.1:11211', ], username='admin', password='sikret',
                          behaviors={'tcp_nodelay': True, 'ketama': True})


PySmartCacheSettings.cache_client = gimme_the_client
```
Note that `memcached` client must use `pylibmc` client and `redis` client must use `redis` client.

### Defining your own clients
`PySmartCache` comes with `memcached` and `redis` clients implemented. You can implement and use another ones.  
All you have to do is create a `class` for this new client, inheriting from `CacheClient` and define a minimal set of methods.  
Take a look at this example:
```python
from pysmartcache import CacheClient, PySmartCacheSettings


class MyCustomClient(CacheClient):
    _DEFAULT_HOST = '127.0.0.1:1111'
    name = 'custom'  # this is the client's name for lookup. Use something like 'memcached', 'redis', 'rds', 'mongodb', etc

    def get_client(self, host):  # must connect with client and return it
        # line below gets host the right way, so keep it
        # `use_list` must be `True` when you want a list of hosts (for a connection pool, for instance)
        host = PySmartCacheSettings._get_cache_host(host, default=self._DEFAULT_HOST, use_list=False)

        return CreateClientConnection(host)  # that's the important part. =P

    def get(self, key):
        pass

    def set(self, key, value):
        pass  # I strongly suggest you to always set values as a pickle str (this avoid problems with data types, trust me)

    def delete(self, key):
        pass

    def purge(self):
        pass
```

### Creating custom unique representation rules
`PySmartCache` deals with common objects unique representation. This is important in order to generate the cache key.  
You can define you own unique representation for a given object by implementing `__cache_key__` method (as described [here](#defining-cache-uniqueness), but sometimes we have no access to the class itself - for instance, when it is a third-party library.  
On these cases, all you have to do is create a `class` for this unique representation, inheriting from `UniqueRepresentation` and define the `get_unique_representation` method.    
Bear in mind that this method must return a **`string`** if you can deal with the object passed as parameter, and **`None`** otherwise.  
Take a look at this example:
```python
from pysmartcache import UniqueRepresentation


class WildObjectRepresentation(UniqueRepresentation):
    def get_unique_representation(self, obj):
        if isinstance(obj, WildObject):
            return str(obj.weird_identifier)
```
## Contributing
If you like the project and feel that you can contribute for it, feel free!  =]  
I'll be glad and will add your name to the project's authors.

### Preparing environment
Firstly, make sure to install both memcached and redis.  
In order to prepare your environment to development:
```bash
# git clone ...
python setup.py install
pip install -r requirements_test.txt
python setup.py test
```

### Rules to contribute
* Follow the [PEP8](https://www.python.org/dev/peps/pep-0008/).
  * Use 132 characters as line length.
* Readability is more important than performance.
  * If you have to decide between an ugly golden solution and a clean 10% slower one, use the latter.
* Don't abbrv d cod!
  * Never abbreviate the code. Variable names, test cases, class names, method names... please, be verbose.
* Write tests.
