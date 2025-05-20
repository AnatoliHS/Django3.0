# Django Cache Directory

This directory is used for Django's file-based caching system.

## Purpose

- Stores cached data for improving admin performance
- Primarily caches expensive queries from the `ParticipationInline` admin class
- Also used for `YearSelectorWidget` data caching

## Guidelines

- Do not manually delete or modify files in this directory
- Cache invalidation is handled automatically by the application code
- All files except this README.md should be excluded from version control

## Maintenance

The cache can be cleared by:
1. Deleting all files (except this README.md) in this directory
2. Restarting the Django application server
3. Using Django management command: `python manage.py clear_cache`
