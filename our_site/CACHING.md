# Django Admin Performance Caching

This document describes the caching implementation for improving Django admin performance, particularly for `ParticipationInline` and `YearSelectorWidget`.

## Overview

The caching implementation provides significant performance improvements for:

1. Group and Person admin pages with `ParticipationInline`
2. Year selection widgets in forms

## Cache Configuration

The Django application uses a filesystem-based cache located at `our_site/tmp/`. The cache is configured in `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'tmp'),
        'TIMEOUT': 60 * 60 * 24 * 7,  # 1 week cache timeout
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # Maximum number of entries in the cache
        }
    }
}
```

## What's Being Cached

1. **ParticipationInline Querysets**: Each Group and Person's participation list is cached with appropriate sorting and annotations.
   - Cache keys: `participation_inline_group_<id>` and `participation_inline_person_<id>`

2. **YearSelectorWidget Year Choices**: The available school years shown in the widget are cached.
   - Cache key: `year_selector_choices`

## Cache Invalidation

The caching system includes automatic invalidation when data is changed:

1. When a Participation is created, updated, or deleted, the cache for relevant Group and Person is cleared.
2. When a Person's role changes, it affects sorting order, so the cache for all groups they participate in is cleared.
3. The YearSelector cache is long-lived (30 days) since it only needs to be updated once per year.

## Management Commands

Two management commands are provided for cache management:

### 1. Clear Cache Command

To clear the cache:

```bash
python manage.py clear_cache
```

To clear specific cache keys or patterns:

```bash
# Clear all group participation caches
python manage.py clear_cache --specific="participation_inline_group_*"

# Clear all person participation caches
python manage.py clear_cache --specific="participation_inline_person_*"

# Clear year selector cache
python manage.py clear_cache --specific="year_selector_choices"
```

### 2. Warm Cache Command

To pre-warm the cache:

```bash
# Warm all caches
python manage.py warm_cache

# Warm only group participation caches
python manage.py warm_cache --groups

# Warm only person participation caches
python manage.py warm_cache --persons

# Warm only year selector cache
python manage.py warm_cache --years
```

## Maintenance Recommendations

1. Run `warm_cache` after any database migration that affects Groups, Persons, or Participations.
2. Run `warm_cache` during deployment to ensure optimal performance from the start.
3. Consider setting up a daily/weekly cron job to run `warm_cache` during off-peak hours to ensure the cache remains fresh.

## Performance Impact

The caching implementation provides the following benefits:

1. Faster loading of Group and Person admin pages with large numbers of participants
2. Reduced database load, especially for repeated queries
3. Improved scalability for sites with many users and groups

## Future Improvements

Possible future enhancements:

1. Adding Redis or Memcached for multi-server setups
2. Implementing cache versioning for better invalidation control
3. Adding more granular caching for other expensive queries
