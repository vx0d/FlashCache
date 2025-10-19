# flashcache.py
# Single-file caching utility

from collections import OrderedDict, defaultdict
from functools import wraps
from time import time
import threading
import inspect
import asyncio
import types
from typing import Any, Callable, Optional

class _CacheEntry:
    def __init__(self, value: Any, expires_at: Optional[float]):
        self.value = value
        self.expires_at = expires_at
        self.created_at = time()

class _LFUState:
    def __init__(self):
        self.freq = defaultdict(int)
        self.last_used = {}

def _make_key(args, kwargs):
    try:
        key = (args, tuple(sorted(kwargs.items())))
        hash(key)
        return key
    except Exception:
        try:
            return (repr(args), repr(sorted(kwargs.items())))
        except Exception:
            return str((args, kwargs))

def flashcache(ttl: Optional[float] = None, maxsize: int = 128, strategy: str = "lru"):
    if strategy not in ("lru", "lfu"):
        raise ValueError("strategy must be 'lru' or 'lfu'")

    def decorator(func: Callable):
        is_coro = inspect.iscoroutinefunction(func)
        lock = threading.RLock()
        store = OrderedDict()
        lfu = _LFUState()
        hits = 0
        misses = 0

        def _prune_expired():
            now = time()
            remove = []
            for k, entry in list(store.items()):
                if entry.expires_at is not None and entry.expires_at <= now:
                    remove.append(k)
            for k in remove:
                store.pop(k, None)
                if strategy == "lfu":
                    lfu.freq.pop(k, None)
                    lfu.last_used.pop(k, None)

        def _evict_if_needed():
            while len(store) > maxsize:
                if strategy == "lru":
                    store.popitem(last=False)
                else:
                    min_key = None
                    min_score = None
                    for k in store.keys():
                        f = lfu.freq.get(k, 0)
                        lu = lfu.last_used.get(k, 0)
                        score = (f, lu)
                        if min_score is None or score < min_score:
                            min_score = score
                            min_key = k
                    if min_key is None:
                        store.popitem(last=False)
                    else:
                        store.pop(min_key, None)
                        lfu.freq.pop(min_key, None)
                        lfu.last_used.pop(min_key, None)

        def _get_info():
            return {
                "hits": hits,
                "misses": misses,
                "size": len(store),
                "maxsize": maxsize,
                "strategy": strategy,
                "ttl": ttl,
            }

        def _cache_clear():
            with lock:
                store.clear()
                lfu.freq.clear()
                lfu.last_used.clear()

        def _cache_invalidate(*a, **kw):
            k = _make_key(a, kw)
            with lock:
                store.pop(k, None)
                lfu.freq.pop(k, None)
                lfu.last_used.pop(k, None)

        def _cache_keys():
            with lock:
                return list(store.keys())

        async def _async_wrapper(*a, **kw):
            nonlocal hits, misses
            k = _make_key(a, kw)
            async_lock = None
            if isinstance(lock, threading.RLock):
                pass
            with lock:
                _prune_expired()
                entry = store.get(k)
                if entry is not None:
                    expires = entry.expires_at
                    if expires is None or expires > time():
                        hits += 1
                        if strategy == "lru":
                            store.move_to_end(k, last=True)
                        else:
                            lfu.freq[k] += 1
                            lfu.last_used[k] = time()
                        return entry.value
                    else:
                        store.pop(k, None)
                        lfu.freq.pop(k, None)
                        lfu.last_used.pop(k, None)
                misses += 1
            result = await func(*a, **kw)
            expires_at = None if ttl is None else time() + ttl
            entry = _CacheEntry(result, expires_at)
            with lock:
                store[k] = entry
                if strategy == "lru":
                    store.move_to_end(k, last=True)
                else:
                    lfu.freq[k] += 1
                    lfu.last_used[k] = time()
                _evict_if_needed()
            return result

        def _sync_wrapper(*a, **kw):
            nonlocal hits, misses
            k = _make_key(a, kw)
            with lock:
                _prune_expired()
                entry = store.get(k)
                if entry is not None:
                    expires = entry.expires_at
                    if expires is None or expires > time():
                        hits += 1
                        if strategy == "lru":
                            store.move_to_end(k, last=True)
                        else:
                            lfu.freq[k] += 1
                            lfu.last_used[k] = time()
                        return entry.value
                    else:
                        store.pop(k, None)
                        lfu.freq.pop(k, None)
                        lfu.last_used.pop(k, None)
                misses += 1
            result = func(*a, **kw)
            expires_at = None if ttl is None else time() + ttl
            entry = _CacheEntry(result, expires_at)
            with lock:
                store[k] = entry
                if strategy == "lru":
                    store.move_to_end(k, last=True)
                else:
                    lfu.freq[k] += 1
                    lfu.last_used[k] = time()
                _evict_if_needed()
            return result

        wrapper = _async_wrapper if is_coro else _sync_wrapper
        wrapped = wraps(func)(wrapper)
        wrapped.cache_clear = _cache_clear
        wrapped.cache_invalidate = _cache_invalidate
        wrapped.cache_info = _get_info
        wrapped.cache_keys = _cache_keys
        return wrapped

    return decorator
