from django.apps import AppConfig
from django.conf import settings
import os
from django.core.management import call_command
from django.contrib.auth import get_user_model
import sys


class ConstanceConfig(AppConfig):
    """
    Custom configuration for the Constance app to rename it to 'Settings' in the admin.
    """
    name = 'constance'
    verbose_name = 'Settings'


class OurSiteConfig(AppConfig):
    """
    App configuration for the our_site app to discover management commands.
    """
    name = 'our_site'
    verbose_name = 'Site Configuration'

    def ready(self):
        """
        Called when the application is ready.
        Performs initial setup if the database does not exist.
        """
        # Skip database initialization during certain management commands
        # where database access might cause issues
        if 'migrate' in sys.argv or 'collectstatic' in sys.argv or 'makemigrations' in sys.argv:
            return

        # Only run in the main process to avoid issues with auto-reload
        if not settings.DEBUG or os.environ.get('RUN_MAIN') == 'true':
            try:
                db_path = settings.DATABASES['default']['NAME']
                # Ensure the directory for the SQLite file exists
                db_dir = os.path.dirname(db_path)
                if not os.path.exists(db_dir):
                    os.makedirs(db_dir)

                if not os.path.exists(db_path):
                    print(f"\n[OurSiteConfig] Database not found at {db_path}. Initializing...")
                    # Apply migrations
                    call_command('migrate', interactive=False, verbosity=1)
                    print("[OurSiteConfig] Migrations applied.")

                    # Create superuser
                    User = get_user_model()
                    if not User.objects.filter(username='admin').exists():
                        User.objects.create_superuser('admin', '', 'SteepRiver01')
                        print("[OurSiteConfig] Default admin user created with username 'admin' and password 'SteepRiver01'.")
                    else:
                        print("[OurSiteConfig] Admin user already exists.")
                else:
                    # Only during normal startup, not during development server reload
                    if os.environ.get('RUN_MAIN') != 'true':
                        print(f"[OurSiteConfig] Database found at {db_path}.")
            except Exception as e:
                print(f"[OurSiteConfig] Error during database initialization: {str(e)}")