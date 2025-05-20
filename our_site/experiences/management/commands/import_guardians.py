import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from experiences.models import Person, GuardianStudent
from django.db import transaction

class Command(BaseCommand):
    help = 'Import guardian-student relationships from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run the import in dry-run mode (no changes will be made)',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('Running in dry-run mode - no changes will be made'))

        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                
                # Validate CSV headers
                required_fields = ['guardian_email', 'student_email', 'relationship']
                missing_fields = [field for field in required_fields if field not in reader.fieldnames]
                if missing_fields:
                    self.stderr.write(self.style.ERROR(
                        f'Missing required fields in CSV: {", ".join(missing_fields)}'
                    ))
                    return

                # Process each row
                with transaction.atomic():
                    for row in reader:
                        try:
                            # Get guardian
                            guardian_user = User.objects.get(email=row['guardian_email'])
                            guardian = Person.objects.get(user=guardian_user)

                            # Get student
                            student_user = User.objects.get(email=row['student_email'])
                            student = Person.objects.get(user=student_user)

                            # Check if relationship already exists
                            relationship, created = GuardianStudent.objects.get_or_create(
                                guardian=guardian,
                                student=student,
                                defaults={
                                    'relationship': row['relationship'],
                                    'notes': row.get('notes', ''),
                                    'is_active': True
                                }
                            )

                            if created:
                                action = 'Created'
                            else:
                                if not relationship.is_active:
                                    relationship.is_active = True
                                    relationship.save()
                                    action = 'Reactivated'
                                else:
                                    action = 'Already exists'

                            self.stdout.write(self.style.SUCCESS(
                                f'{action}: {guardian} -> {student} ({row["relationship"]})'
                            ))

                        except User.DoesNotExist as e:
                            self.stderr.write(self.style.WARNING(
                                f'Skipping row - User not found: {str(e)}'
                            ))
                        except Person.DoesNotExist as e:
                            self.stderr.write(self.style.WARNING(
                                f'Skipping row - Person not found: {str(e)}'
                            ))
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(
                                f'Error processing row: {str(e)}'
                            ))

                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING('Dry run completed - no changes were made'))
                else:
                    self.stdout.write(self.style.SUCCESS('Import completed successfully'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}')) 