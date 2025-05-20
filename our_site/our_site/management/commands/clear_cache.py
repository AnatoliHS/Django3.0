from django.core.management.base import BaseCommand
from django.core.cache import cache
import os
import glob
from django.conf import settings

class Command(BaseCommand):
    help = 'Clears the Django cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--specific',
            action='store',
            dest='cache_key',
            help='Clear a specific cache key or pattern (e.g., "participation_inline_*")',
        )

    def handle(self, *args, **options):
        specific_key = options.get('cache_key')
        
        if specific_key:
            # If using a pattern like "participation_inline_*", we need to iterate through keys
            if '*' in specific_key:
                pattern = specific_key.replace('*', '')
                # Get all keys and filter those matching the pattern
                # This is a bit of a hack as Django's cache API doesn't support wildcard deletion
                # For the filesystem cache, we could directly search for files, but this is more generic
                
                # For filesystem cache, we can use glob directly
                if hasattr(settings, 'CACHES') and settings.CACHES.get('default', {}).get('BACKEND') == 'django.core.cache.backends.filebased.FileBasedCache':
                    cache_dir = settings.CACHES['default']['LOCATION']
                    pattern_files = glob.glob(os.path.join(cache_dir, f"*{pattern}*"))
                    for file_path in pattern_files:
                        try:
                            os.remove(file_path)
                            self.stdout.write(f"Removed cache file: {os.path.basename(file_path)}")
                        except OSError as e:
                            self.stderr.write(f"Error removing file {file_path}: {e}")
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully cleared cache keys matching '{specific_key}'")
                    )
                else:
                    # For other cache backends, we fall back to clearing the whole cache
                    # as there's no standard way to get all keys
                    cache.clear()
                    self.stdout.write(
                        self.style.WARNING(f"Wildcard deletion not supported for this cache backend. Cleared entire cache.")
                    )
            else:
                # Delete a specific key
                cache.delete(specific_key)
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully cleared cache key '{specific_key}'")
                )
        else:
            # Clear the entire cache
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared entire cache')
            )
