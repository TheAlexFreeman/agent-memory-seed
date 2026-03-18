---
source: external-research
origin_session: chats/2026/03/18/chat-001
created: 2026-03-18
last_verified: 2026-03-18
trust: low
---

# Django Caching with Redis

Covers Django's cache framework and Redis-specific configuration. Relevant because Alex uses Redis for Celery's broker/result backend — same Redis instance can (carefully) serve caching too.

## Cache backend setup (django-redis)

Django ships with a Redis cache backend since Django 4.0 (`django.core.cache.backends.redis.RedisCache`), but `django-redis` (jazzband) remains the more feature-rich option. Most production setups use `django-redis`.

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # db=1, leave db=0 for Celery
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MAX_CONNECTIONS": 100,
            "RETRY_ON_TIMEOUT": True,
            "IGNORE_EXCEPTIONS": True,  # degraded mode: cache miss on Redis error
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "myapp",
        "TIMEOUT": 300,  # 5 minutes default TTL
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 86400,  # 24 hours
    },
}
```

**DB segregation:** Use separate Redis databases (or separate Redis instances in production) for caching, sessions, and Celery. Prevents cache flushes from killing Celery queues.

## Cache API

```python
from django.core.cache import cache

# Set / get:
cache.set("user:42:profile", data, timeout=600)
value = cache.get("user:42:profile", default=None)

# Set only if key doesn't exist:
cache.add("lock:resource_id", True, timeout=30)

# Delete:
cache.delete("user:42:profile")

# Increment/decrement (atomic):
cache.set("page_views", 0)
cache.incr("page_views")
cache.decr("page_views")

# Multiple keys at once:
cache.set_many({"a": 1, "b": 2}, timeout=300)
values = cache.get_many(["a", "b"])
cache.delete_many(["a", "b"])

# Versioning:
cache.set("key", value, version=2)
cache.get("key", version=2)
```

## Cache decorators

```python
from django.views.decorators.cache import cache_page, never_cache
from django.utils.decorators import method_decorator

# Cache an entire view for 15 minutes:
@cache_page(60 * 15)
def my_view(request):
    ...

# Class-based view:
@method_decorator(cache_page(60 * 15), name="dispatch")
class MyView(View):
    ...

# Prevent caching:
@never_cache
def private_view(request):
    ...
```

## Cache per-site vs. per-view vs. template fragment

```python
# Per-site: add to MIDDLEWARE (caches entire site)
MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    ...
    "django.middleware.cache.FetchFromCacheMiddleware",
]
CACHE_MIDDLEWARE_SECONDS = 600

# Template fragment:
{% load cache %}
{% cache 500 sidebar user.id %}
    ... expensive sidebar rendering ...
{% endcache %}
```

## Pattern: cache-aside (most common)

```python
def get_user_stats(user_id: int) -> dict:
    cache_key = f"user:{user_id}:stats"
    data = cache.get(cache_key)
    if data is None:
        data = compute_expensive_stats(user_id)
        cache.set(cache_key, data, timeout=300)
    return data
```

## Pattern: cache stampede prevention

When many requests simultaneously miss a hot key that just expired:

```python
import time

def get_with_lock(cache_key, compute_fn, timeout=300):
    data = cache.get(cache_key)
    if data is not None:
        return data

    lock_key = f"lock:{cache_key}"
    # Try to acquire lock:
    if cache.add(lock_key, True, timeout=30):
        try:
            data = compute_fn()
            cache.set(cache_key, data, timeout=timeout)
        finally:
            cache.delete(lock_key)
        return data
    else:
        # Another process is computing — wait and retry:
        time.sleep(0.1)
        return cache.get(cache_key)  # may still be None on timeout
```

For high-traffic cases, consider "probabilistic early expiration" or a dedicated library like `django-cache-lock`.

## Session backend via Redis

```python
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"  # use dedicated session cache
```

This is significantly faster than DB-backed sessions and scales well horizontally.

## Cache invalidation patterns

```python
# Key-based invalidation (explicit):
cache.delete(f"user:{user_id}:profile")

# Pattern-based invalidation (django-redis specific):
from django_redis import get_redis_connection
redis = get_redis_connection("default")
keys = redis.keys("myapp:user:*:profile")
if keys:
    redis.delete(*keys)
```

**Warning:** Pattern deletion (`KEYS *`) blocks Redis. Use `SCAN` for production. django-redis wraps this, but be careful on large key spaces.

## Separating cache from Celery on the same Redis

Practical Docker Compose setup:

```yaml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru

# In Django settings:
# CACHES → db=1 (cache)
# SESSION → db=2 (sessions)
# CELERY_BROKER_URL → redis://redis:6379/0 (Celery)
# CELERY_RESULT_BACKEND → redis://redis:6379/0 (or db=3)
```

For production, use separate Redis instances — different eviction policies (LRU for cache, no eviction for Celery broker).

## Cache versioning for safe deploys

```python
CACHES = {
    "default": {
        ...
        "KEY_PREFIX": "v2",  # bump on breaking schema changes
        "VERSION": 1,
    }
}
```

Incrementing `KEY_PREFIX` effectively invalidates all cached data without a flush.

Last updated: 2026-03-18
