"""
Caching utilities and decorators for optimized database queries.
Handles N+1 query prevention and frequently accessed data caching.
"""

from django.core.cache import cache
import hashlib
from functools import wraps


# Cache timeout constants
CACHE_TIMEOUT_SHORT = 300  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 3600  # 1 hour
CACHE_TIMEOUT_LONG = 86400  # 24 hours


def cache_key(*args, **kwargs):
    """Generate a consistent cache key from arguments."""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def invalidate_cache(*patterns):
    """Invalidate cache by patterns."""
    # For production, use cache.delete_pattern() with redis
    # This is a simple implementation
    for pattern in patterns:
        cache.delete(pattern)


def cache_job_stats(user_id=None):
    """Cache job statistics."""
    cache_key_str = f"job_stats:{user_id}" if user_id else "job_stats:global"

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cached = cache.get(cache_key_str)
            if cached:
                return cached

            result = func(*args, **kwargs)
            cache.set(cache_key_str, result, CACHE_TIMEOUT_MEDIUM)
            return result
        return wrapper
    return decorator


def cache_user_profile(func):
    """Cache user profile data."""
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            cache_key_str = f"user_profile:{request.user.id}"
            cached = cache.get(cache_key_str)
            if cached:
                return cached

            result = func(self, request, *args, **kwargs)
            cache.set(cache_key_str, result, CACHE_TIMEOUT_MEDIUM)
            return result

        return func(self, request, *args, **kwargs)
    return wrapper


class CacheInvalidatorMixin:
    """Mixin to automatically invalidate related caches on model save/delete."""

    cache_keys_to_invalidate = []

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invalidate_caches()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.invalidate_caches()

    def invalidate_caches(self):
        """Invalidate all related cache keys."""
        for key_pattern in self.cache_keys_to_invalidate:
            cache.delete(key_pattern)


class QueryOptimizationMixin:
    """Mixin for query optimization with select_related and prefetch_related."""

    select_related_fields = []
    prefetch_related_fields = []

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)

        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        return queryset
