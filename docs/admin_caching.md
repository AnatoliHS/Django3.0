# Django Admin Caching Implementation

This document outlines the caching strategy implemented to improve the performance of the Django admin interface, particularly for `ParticipationInline` and `YearSelectorWidget`.

## Overview

We've implemented filesystem-based caching to reduce database load and improve page load times in the Django admin. The caching system targets two main areas:

1. **ParticipationInline Queryset Caching**: Caches the sorted and annotated querysets used in the Group and Person admin views.
2. **YearSelectorWidget Data Caching**: Caches the year choices used in form fields.

## Configuration

The caching system is configured in the Django settings (`our_site/our_site/settings.py`):

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

Cache files are stored in the `our_site/tmp` directory, which is included in `.gitignore` to prevent cache files from being committed to the repository.

## Cache Keys

The following cache key patterns are used:

- `participation_inline_group_{id}`: Caches the `ParticipationInline` queryset for a specific Group.
- `participation_inline_person_{id}`: Caches the `ParticipationInline` queryset for a specific Person.
- `year_selector_choices`: Caches the list of year choices used in the `YearSelectorWidget`.

## Cache Invalidation

Cache invalidation is implemented in the `save_model()`, `delete_model()`, and `save_related()` methods of the relevant admin classes:

- **GroupAdmin**: Clears the cache when a Group is saved, deleted, or when its members change.
- **PersonAdmin**: Clears the cache when a Person is saved or deleted. Also clears caches for any Groups the Person is a member of.
- **ParticipationAdmin**: Clears the caches for the related Group and Person when a Participation record is saved or deleted.

The `YearSelectorWidget` cache is set to expire after 30 days but can be manually cleared if needed.

## Management Commands

Two management commands are provided to manage the caching system:

1. **clear_cache**: Clears the cache partially or completely.
   ```bash
   # Clear all caches
   python manage.py clear_cache
   
   # Clear specific cache
   python manage.py clear_cache --specific=participation_inline_group_42
   
   # Clear all group participation caches
   python manage.py clear_cache --specific=participation_inline_group_*
   ```

2. **warm_cache**: Pre-warms the cache for faster initial load times.
   ```bash
   # Warm all caches
   python manage.py warm_cache
   
   # Warm only group caches
   python manage.py warm_cache --groups
   
   # Warm only person caches
   python manage.py warm_cache --persons
   
   # Warm only year selector caches
   python manage.py warm_cache --years
   ```

## Deployment Recommendations

1. **Cache Directory**: Ensure the `our_site/tmp` directory exists and is writable by the application process.
2. **Initial Cache Warming**: Run `python manage.py warm_cache` after deployment to pre-warm the cache.
3. **Periodic Cache Maintenance**: Consider setting up a cron job to run `warm_cache` periodically (e.g., nightly) to ensure the cache stays fresh.

## Monitoring and Troubleshooting

If admin pages show stale data, try clearing the cache:

```bash
python manage.py clear_cache
```

For performance issues, check:
1. The size of the cache directory (`our_site/tmp`)
2. The `MAX_ENTRIES` setting to ensure it's appropriate for your data size
3. Database query logs to confirm that queries are being cached

## Performance Impact

This caching implementation should significantly improve admin performance, especially for:
- Loading the Group admin page with many participations
- Loading the Person admin page with many participations 
- Rendering forms with the `YearSelectorWidget`

The improvement will be most noticeable for users who frequently access the same data.
