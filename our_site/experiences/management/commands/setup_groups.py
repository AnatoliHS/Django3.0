from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from experiences.models import Person, Group as ActivityGroup

class Command(BaseCommand):
    help = 'Creates the Administrators group and sets up permissions'

    def handle(self, *args, **options):
        # Create Administrators group if it doesn't exist
        administrators_group, created = Group.objects.get_or_create(name='Administrators')
        
        # Get all permissions for Person model
        person_content_type = ContentType.objects.get_for_model(Person)
        person_permissions = Permission.objects.filter(content_type=person_content_type)
        
        # Get all permissions for Group model
        group_content_type = ContentType.objects.get_for_model(ActivityGroup)
        group_permissions = Permission.objects.filter(content_type=group_content_type)
        
        # Add all Person and Group model permissions to Administrators group
        administrators_group.permissions.add(*person_permissions)
        administrators_group.permissions.add(*group_permissions)
        
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Administrators group'))
        else:
            self.stdout.write(self.style.SUCCESS('Successfully updated Administrators group permissions')) 