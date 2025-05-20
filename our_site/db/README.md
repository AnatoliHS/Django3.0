# Database File: db.sqlite3

The file `db.sqlite3` is the SQLite database used to store persistent data for the application. This file is auto-generated when you initialize your project (for example, when running migrations in a Django project or setting up your environment). Do **not** manually modify this file, as it contains critical runtime data.

Place the `db.sqlite3` file here in the project's db directory so that it can be accessed consistently by your application's components.

## Alternative Database Setup: MariaDB

If you prefer using MariaDB as your database backend rather than SQLite, follow these steps:

1. Install the required MariaDB client library for Django (e.g., mysqlclient or PyMySQL).

2. Update your project's database configuration (commonly found in settings.py):

    ```
    DATABASES = {
         'default': {
              'ENGINE': 'django.db.backends.mysql',
              'NAME': 'your_database_name',
              'USER': 'your_username',
              'PASSWORD': 'your_password',
              'HOST': 'localhost',
              'PORT': '3306',
              'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
              },
         }
    }
    ```

3. Run your migrations to set up the database schema:

    ```
    python manage.py migrate
    ```