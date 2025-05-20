# Generated manually on 2025-05-16

from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration checks if the participation_badges table exists and
    recreates it if it doesn't, fixing the "no such table" error.
    """

    dependencies = [
        ('experiences', '0016_person_cached_str'),
    ]

    operations = [
        migrations.RunSQL(
            # Check if table exists, if not create it
            """
            CREATE TABLE IF NOT EXISTS "experiences_participation_badges" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "participation_id" integer NOT NULL REFERENCES "experiences_participation" ("id") DEFERRABLE INITIALLY DEFERRED,
                "badges_id" integer NOT NULL REFERENCES "experiences_badges" ("id") DEFERRABLE INITIALLY DEFERRED
            );
            CREATE INDEX IF NOT EXISTS "experiences_participation_badges_participation_id_9ccfe397" ON "experiences_participation_badges" ("participation_id");
            CREATE INDEX IF NOT EXISTS "experiences_participation_badges_badges_id_3df36a2c" ON "experiences_participation_badges" ("badges_id");
            CREATE UNIQUE INDEX IF NOT EXISTS "experiences_participation_badges_participation_id_badges_id_e3a8eeac_uniq" ON "experiences_participation_badges" ("participation_id", "badges_id");
            """,
            # Reverse SQL (does nothing for safety)
            """SELECT 1;"""
        ),
    ]
