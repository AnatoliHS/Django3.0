#!/usr/bin/env python
"""
This is a debugging script to verify facilitator queries directly.
Run this script from the Django shell:

python manage.py shell < debug_facilitators.py

"""
from experiences.models import Group, Person, Role, Participation
import json
from django.utils import timezone

print("=" * 50)
print("DEBUGGING FACILITATOR QUERIES")
print("=" * 50)

# Get current school year
current_date = timezone.now()
current_year = current_date.year
if current_date.month < 9:
    school_year = current_year - 1
else:
    school_year = current_year

print(f"Current date: {current_date}")
print(f"School year: {school_year}")

# Get all groups
groups = Group.objects.all()
print(f"Found {groups.count()} groups")

# Check facilitator role
facilitator_roles = Role.objects.filter(title__iexact='facilitator')
print(f"Found {facilitator_roles.count()} facilitator roles: {[r.title for r in facilitator_roles]}")

# Check each group
for group in groups:
    print("\n" + "-" * 50)
    print(f"Group: {group.name} (ID: {group.pk})")
    
    # Get members
    members = group.members.all()
    print(f"  Total members: {members.count()}")
    
    # Get facilitators using the original query
    facilitators = members.filter(
        role__title__iexact='facilitator'
    ).distinct()
    
    print(f"  Facilitators: {facilitators.count()}")
    
    if facilitators:
        for f in facilitators:
            print(f"    - {f.user.get_full_name() or f.user.username} (Role: {f.role.title})")
    
    # Alternative query approach
    alt_facilitators = Person.objects.filter(
        groups=group,
        role__title__iexact='facilitator'
    ).distinct()
    
    print(f"  Alt Facilitators: {alt_facilitators.count()}")
    
    if alt_facilitators:
        for f in alt_facilitators:
            print(f"    - {f.user.get_full_name() or f.user.username} (Role: {f.role.title})")

print("\nDone debugging facilitator queries")
