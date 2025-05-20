from django.contrib import admin
from django.utils.html import format_html
from .models import *
from django.core.cache import cache
from django import forms
from django.shortcuts import render
from django.urls import path, reverse
from django.contrib import messages
import csv
import random
import string
import zipfile
import io
import os
from PIL import Image
from django.core.files.base import ContentFile
from io import TextIOWrapper, StringIO
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Case, When, Value, IntegerField
from .admin_widgets import YearSelectorWidget
from .forms import PersonForm


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 0
    exclude = ('is_public',)
    show_change_link = True

    # Exclude the badges field from the inline
    fields = ('person', 'group', 'hours', 'special_recognition', 'elementary', 'senior', 'years',)

    formfield_overrides = {
        models.JSONField: {'widget': YearSelectorWidget()},
    }
    
    def get_formset(self, request, obj=None, **kwargs):
        if obj:
            request._parent_obj = obj
        return super().get_formset(request, obj, **kwargs)
    
    def get_queryset(self, request):
        parent_obj = getattr(request, '_parent_obj', None)
        if not parent_obj:
            return super().get_queryset(request)
        
        # Generate cache key
        parent_model = parent_obj.__class__.__name__.lower()
        parent_id = parent_obj.pk
        page = request.GET.get('page', 1)
        cache_key = f'participation_inline_{parent_model}_{parent_id}_page{page}'
        
        # Try to get cached queryset
        cached_queryset = cache.get(cache_key)
        if cached_queryset is not None:
            return cached_queryset
        
        # Optimize base queryset with select_related and only
        queryset = super().get_queryset(request).select_related(
            'person',
            'person__user',
            'person__role'
        ).only(
            'id',
            'person__id',
            'person__user__first_name',
            'person__user__last_name',
            'person__role__id',
            'person__role__title',
            'years',
            'hours',
            'special_recognition'
        )
        
        # Filter by parent object
        if parent_model == 'group':
            queryset = queryset.filter(group_id=parent_id)
        elif parent_model == 'person':
            queryset = queryset.filter(person_id=parent_id)
        
        # Optimize sorting by using a more efficient approach
        facilitator_ids = cache.get('facilitator_role_ids')
        if facilitator_ids is None:
            facilitator_ids = list(Role.objects.filter(title__iexact='facilitator').values_list('id', flat=True))
            cache.set('facilitator_role_ids', facilitator_ids, 3600)  # Cache for 1 hour
        
        if facilitator_ids:
            # Use a more efficient sorting approach
            queryset = queryset.extra(
                select={
                    'sort_order': f"""
                        CASE 
                            WHEN experiences_person.role_id IN ({','.join(map(str, facilitator_ids))}) THEN 1 
                            ELSE 2 
                        END
                    """
                },
                order_by=['sort_order', 'person__user__first_name', 'person__user__last_name']
            )
        else:
            queryset = queryset.order_by('person__user__first_name', 'person__user__last_name')
        
        # Cache the queryset with a shorter TTL for better data freshness
        cache.set(cache_key, queryset, 300)  # Cache for 5 minutes
        
        return queryset
        
    def has_add_permission(self, request, obj=None):
        if obj and obj.__class__.__name__.lower() == 'group':
            # Use a more efficient count query
            count_key = f'participation_count_group_{obj.pk}'
            count = cache.get(count_key)
            if count is None:
                count = Participation.objects.filter(group_id=obj.pk).count()
                cache.set(count_key, count, 300)  # Cache for 5 minutes
                
            if count > 500:
                return False
                
        return True


class VisibilityModelAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'visibility_badge', 'last_modified')
    list_filter = ('is_public',)
    actions = ['make_public', 'make_private']
    
    def get_name(self, obj):
        return str(obj)
    get_name.short_description = 'Name'
    
    def visibility_badge(self, obj):
        if obj.is_public:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 10px;">'
                '✓&NonBreakingSpace;Public</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 10px;">'
            '✕&NonBreakingSpace;Private</span>'
        )
    visibility_badge.short_description = 'Visibility'
    
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} items are now public.')
    make_public.short_description = "Make selected items public"
    
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} items are now private.')
    make_private.short_description = "Make selected items private"


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSV File')
    create_users = forms.BooleanField(required=False, label='Create new users')


def generate_password(length=10):
    """Generate a random pronounceable password"""
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    first_part = ''.join(random.choice(consonants) + random.choice(vowels) for _ in range(length//2))
    number_part = ''.join(random.choice(string.digits) for _ in range(2))
    special_char = random.choice('!@#$%^&*')
    return first_part.capitalize() + number_part + special_char


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'description')
    list_filter = ('is_active',)
    search_fields = ('title',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # If this is an update and title changed, we need to clear caches that depend on role titles
        if change and 'title' in form.changed_data:
            # Get all persons with this role
            affected_persons = Person.objects.filter(role=obj)
            for person in affected_persons:
                # Clear person cache
                cache.delete(f'participation_inline_person_{person.pk}')
                
                # Clear cache for all groups this person is in
                for group in person.groups.all():
                    cache.delete(f'participation_inline_group_{group.pk}')
    
    def delete_model(self, request, obj):
        # Get all persons with this role before deleting
        affected_persons = list(Person.objects.filter(role=obj).values_list('id', flat=True))
        affected_groups = set()
        
        # Get all groups these persons are in
        for person_id in affected_persons:
            person_groups = Group.objects.filter(members__id=person_id)
            affected_groups.update(person_groups.values_list('id', flat=True))
        
        super().delete_model(request, obj)
        
        # Clear caches
        for person_id in affected_persons:
            cache.delete(f'participation_inline_person_{person_id}')
        
        for group_id in affected_groups:
            cache.delete(f'participation_inline_group_{group_id}')


class GuardianStudentInline(admin.TabularInline):
    model = GuardianStudent
    fk_name = 'student'
    extra = 0  # Only show new entries when admin clicks the add button
    verbose_name = "Guardian"
    verbose_name_plural = "Guardians"


class StudentGuardianInline(admin.TabularInline):
    model = GuardianStudent
    fk_name = 'guardian'
    extra = 0  # Only show new entries when admin clicks the add button
    verbose_name = "Student"
    verbose_name_plural = "Students"


@admin.register(GuardianStudent)
class GuardianStudentAdmin(admin.ModelAdmin):
    list_display = ('guardian', 'relationship', 'student', 'is_active', 'date_added')
    list_filter = ('is_active', 'relationship', 'date_added')
    search_fields = ('guardian__user__username', 'guardian__user__first_name', 'guardian__user__last_name',
                    'student__user__username', 'student__user__first_name', 'student__user__last_name')
    raw_id_fields = ('guardian', 'student')
    date_hierarchy = 'date_added'

    def has_change_permission(self, request, obj=None):
        if not obj:  # This is the list view
            return True
        # Superusers can edit anything
        if request.user.is_superuser:
            return True
        # Administrators can edit any relationship
        if request.user.groups.filter(name='Administrators').exists():
            return True
        # Guardians can edit their own relationships
        return obj and (obj.guardian.user == request.user or obj.student.user == request.user)

    def has_delete_permission(self, request, obj=None):
        if not obj:  # This is the list view
            return True
        # Only superusers and administrators can delete
        return request.user.is_superuser or request.user.groups.filter(name='Administrators').exists()


@admin.register(Person)
class PersonAdmin(VisibilityModelAdmin):
    form = PersonForm
    change_list_template = "admin/person_changelist.html"
    
    def get_fieldsets(self, request, obj=None):
        fields = ['user', 'first_name', 'last_name', 'email', 'graduating_year', 'role', 'profile_picture', 'is_public']
        return [(None, {'fields': fields})]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make user field not required on add
        if obj is None:
            form.base_fields['user'].required = False
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-people-csv/', 
                 self.admin_site.admin_view(self.import_people_csv_view), 
                 name='experiences_person_import-people-csv'),
                 
            path('import-guardians-csv/', 
                 self.admin_site.admin_view(self.import_guardians_csv_view), 
                 name='experiences_person_import-guardians-csv'),
                 
            path('download-csv-template/', 
                 self.admin_site.admin_view(self.download_csv_template),
                 name='download_people_csv_template'),
                 
            path('download-guardian-csv-template/', 
                 self.admin_site.admin_view(self.download_guardian_csv_template),
                 name='download_guardian_csv_template'),
                 
            path('download-imported-users/', 
                 self.admin_site.admin_view(self.download_imported_users),
                 name='download_imported_users'),
        ]
        return custom_urls + urls
    
    def import_people_csv_view(self, request):
        """View to import people from CSV file."""
        if request.method == 'POST':
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                create_users = form.cleaned_data['create_users']
                
                # Process the CSV file
                csv_file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8-sig')
                csv_reader = csv.DictReader(csv_file_wrapper)
                
                # Validate CSV structure
                required_fields = ['email', 'role']
                for field in required_fields:
                    if field not in csv_reader.fieldnames:
                        messages.error(request, f"CSV file missing required '{field}' column")
                        return HttpResponseRedirect(request.path)
                
                # Track results for display
                created_users = []
                updated_people = 0
                skipped_rows = 0
                errors = []
                
                # Process each row
                for row in csv_reader:
                    try:
                        # Check required fields
                        email = row.get('email', '').strip()
                        role_title = row.get('role', '').strip().lower()  # Normalize role to lowercase
                        
                        if not email or not role_title:
                            errors.append(f"Row {csv_reader.line_num}: Missing required fields")
                            skipped_rows += 1
                            continue
                        
                        # Check if role exists (case-insensitive)
                        try:
                            # Use case-insensitive query
                            role = Role.objects.filter(title__iexact=role_title).first()
                            if not role:
                                raise Role.DoesNotExist
                        except Role.DoesNotExist:
                            errors.append(f"Row {csv_reader.line_num}: Role '{role_title}' does not exist")
                            skipped_rows += 1
                            continue
                        
                        # Get or create user
                        first_name = row.get('first_name', '').strip()
                        last_name = row.get('last_name', '').strip()
                        graduating_year = row.get('graduating_year', '').strip()
                        
                        try:
                            user = User.objects.get(email=email)
                            # Update existing user info if provided
                            if first_name and not user.first_name:
                                user.first_name = first_name
                            if last_name and not user.last_name:
                                user.last_name = last_name
                            user.save()
                            
                        except User.DoesNotExist:
                            if create_users:
                                # Create new user
                                username = email.split('@')[0]
                                # Make sure username is unique
                                base_username = username
                                counter = 1
                                while User.objects.filter(username=username).exists():
                                    username = f"{base_username}{counter}"
                                    counter += 1
                                    
                                # Generate password
                                password = generate_password()
                                
                                # Create user
                                user = User.objects.create_user(
                                    username=username,
                                    email=email,
                                    password=password,
                                    first_name=first_name,
                                    last_name=last_name
                                )
                                
                                created_users.append({
                                    'email': email,
                                    'username': username,
                                    'password': password,
                                    'name': f"{first_name} {last_name}".strip()
                                })
                            else:
                                errors.append(f"Row {csv_reader.line_num}: User with email '{email}' does not exist and create_users is not checked")
                                skipped_rows += 1
                                continue
                        
                        # Get or create person
                        person, created = Person.objects.get_or_create(
                            user=user,
                            defaults={
                                'role': role,
                                'graduating_year': graduating_year if graduating_year else None
                            }
                        )
                        
                        if not created:
                            # Update existing person
                            if graduating_year:
                                person.graduating_year = graduating_year
                            person.role = role
                            person.save()
                            updated_people += 1
                    
                    except Exception as e:
                        errors.append(f"Row {csv_reader.line_num}: {str(e)}")
                        skipped_rows += 1
                
                # Show results
                if created_users:
                    messages.success(request, f"Created {len(created_users)} new users")
                    
                    # Provide CSV download for created users
                    csv_output = StringIO()
                    csv_writer = csv.writer(csv_output)
                    csv_writer.writerow(['Username', 'Email', 'Password', 'Name'])
                    for user_data in created_users:
                        csv_writer.writerow([
                            user_data['username'], 
                            user_data['email'],
                            user_data['password'],
                            user_data['name']
                        ])
                    
                    # Store the CSV data in the session for download
                    request.session['user_import_csv'] = csv_output.getvalue()
                    
                    # Link to download the CSV
                    download_url = reverse('admin:download_imported_users')
                    messages.info(request, format_html(
                        'Download <a href="{}">user credentials CSV</a> to share with new users.', 
                        download_url
                    ))
                
                if updated_people > 0:
                    messages.success(request, f"Updated {updated_people} existing people")
                    
                if skipped_rows > 0:
                    messages.warning(request, f"Skipped {skipped_rows} rows due to errors")
                    
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)
                    
                if len(errors) > 10:
                    messages.error(request, f"... and {len(errors) - 10} more errors")
                    
                return HttpResponseRedirect(reverse('admin:experiences_person_changelist'))
        else:
            form = CSVUploadForm()
            
        context = {
            'title': 'Import People from CSV',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/people_csv_form.html', context)
    
    def import_guardians_csv_view(self, request):
        """View to import guardian-student relations from CSV file."""
        if request.method == 'POST':
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                
                # Process the CSV file
                csv_file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8-sig')
                csv_reader = csv.DictReader(csv_file_wrapper)
                
                # Validate CSV structure
                required_fields = ['guardian_email', 'student_email', 'relationship']
                for field in required_fields:
                    if field not in csv_reader.fieldnames:
                        messages.error(request, f"CSV file missing required '{field}' column")
                        return HttpResponseRedirect(request.path)
                
                # Track results for display
                created_relations = 0
                skipped_rows = 0
                errors = []
                
                # Process each row
                for row in csv_reader:
                    try:
                        # Check required fields
                        guardian_email = row.get('guardian_email', '').strip()
                        student_email = row.get('student_email', '').strip()
                        relationship = row.get('relationship', '').strip()
                        
                        if not guardian_email or not student_email or not relationship:
                            errors.append(f"Row {csv_reader.line_num}: Missing required fields")
                            skipped_rows += 1
                            continue
                        
                        # Check if users exist
                        try:
                            guardian_user = User.objects.get(email=guardian_email)
                        except User.DoesNotExist:
                            errors.append(f"Row {csv_reader.line_num}: Guardian with email '{guardian_email}' not found")
                            skipped_rows += 1
                            continue
                            
                        try:
                            student_user = User.objects.get(email=student_email)
                        except User.DoesNotExist:
                            errors.append(f"Row {csv_reader.line_num}: Student with email '{student_email}' not found")
                            skipped_rows += 1
                            continue
                        
                        # Check if people exist
                        try:
                            guardian = Person.objects.get(user=guardian_user)
                        except Person.DoesNotExist:
                            errors.append(f"Row {csv_reader.line_num}: Guardian person record for '{guardian_email}' not found")
                            skipped_rows += 1
                            continue
                            
                        try:
                            student = Person.objects.get(user=student_user)
                        except Person.DoesNotExist:
                            errors.append(f"Row {csv_reader.line_num}: Student person record for '{student_email}' not found")
                            skipped_rows += 1
                            continue
                        
                        # Create or update the relationship
                        relation, created = GuardianStudent.objects.get_or_create(
                            guardian=guardian,
                            student=student,
                            defaults={'relationship': relationship}
                        )
                        
                        if not created:
                            relation.relationship = relationship
                            relation.save()
                        
                        created_relations += 1
                    
                    except Exception as e:
                        errors.append(f"Row {csv_reader.line_num}: {str(e)}")
                        skipped_rows += 1
                
                # Show results
                if created_relations > 0:
                    messages.success(request, f"Created/updated {created_relations} guardian-student relationships")
                    
                if skipped_rows > 0:
                    messages.warning(request, f"Skipped {skipped_rows} rows due to errors")
                    
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)
                    
                if len(errors) > 10:
                    messages.error(request, f"... and {len(errors) - 10} more errors")
                    
                return HttpResponseRedirect(reverse('admin:experiences_guardianstulient_changelist'))
        else:
            form = CSVUploadForm()
            
        context = {
            'title': 'Import Guardian-Student Relations',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/people_csv_form.html', context)
    
    def download_csv_template(self, request):
        """Provide a downloadable example CSV template."""
        csv_content = "email,role,first_name,last_name,graduating_year\n"
        csv_content += "john.doe@example.com,Student,John,Doe,2026\n"
        csv_content += "jane.smith@example.com,Facilitator,Jane,Smith,"
        
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="people_import_template.csv"'
        return response
    
    def download_guardian_csv_template(self, request):
        """Provide a downloadable guardian relationship CSV template."""
        csv_content = "guardian_email,student_email,relationship\n"
        csv_content += "parent@example.com,student@example.com,Parent\n"
        csv_content += "guardian@example.com,student@example.com,Guardian"
        
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="guardian_relationships_template.csv"'
        return response
    
    def download_imported_users(self, request):
        """Download CSV with user credentials for newly created users."""
        csv_data = request.session.get('user_import_csv', '')
        if not csv_data:
            messages.error(request, "No user data available for download")
            return HttpResponseRedirect(reverse('admin:experiences_person_changelist'))
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="imported_user_credentials.csv"'
        
        # Clear the session data
        del request.session['user_import_csv']
        
        return response

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_guardians(self, obj):
        guardians = obj.guardians.all()
        if not guardians:
            return "-"
        return ", ".join([str(g) for g in guardians])

    def get_students(self, obj):
        students = obj.students.all()
        if not students:
            return "-"
        return ", ".join([str(s) for s in students])

    def get_participations(self, obj):
        """Return a formatted string of participations for this person"""
        # Try to get from cache
        cache_key = f'person_participations_display_{obj.pk}'
        cached_display = cache.get(cache_key)
        
        if cached_display is not None:
            return cached_display
        
        # Get participations with related groups
        participations = obj.participation_set.select_related('group').all()
        if not participations:
            return "-"
            
        # Format the display
        group_names = [p.group.name for p in participations if p.group]
        display = ", ".join(sorted(set(group_names)))
        
        # Cache for a reasonable time
        cache.set(cache_key, display, 3600)  # Cache for 1 hour
        
        return display
    get_participations.short_description = "Participations"

    list_display = ('get_full_name', 'visibility_badge', 'graduating_year', 'role', 'is_active', 
                   'get_participations', 'get_guardians', 'get_students', 'last_modified',
                   'show_activities_publicly', 'show_guardians_publicly')
    list_filter = ('is_public', 'role', 'user__is_active', 'graduating_year', 
                  'guardian_relationships__is_active', 'student_relationships__is_active',
                  'show_activities_publicly', 'show_guardians_publicly')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 
                    'guardian_relationships__student__user__username',
                    'student_relationships__guardian__user__username')
    fields = ('user', 'graduating_year', 'role', 'profile_picture', 'is_public',
              'show_activities_publicly', 'show_guardians_publicly')
    inlines = [ParticipationInline, GuardianStudentInline, StudentGuardianInline]

    def is_active(self, obj):
        return obj.user.is_active
    is_active.boolean = True

    def has_change_permission(self, request, obj=None):
        if not obj:  # This is the list view
            return True
        # Superusers can edit anything
        if request.user.is_superuser:
            return True
        # Administrators can edit any person
        if request.user.groups.filter(name='Administrators').exists():
            return True
        # Users can edit their own profile
        return obj and obj.user == request.user

    def has_delete_permission(self, request, obj=None):
        # Only superusers and administrators can delete
        if not obj:  # This is the list view
            return True
        return request.user.is_superuser or request.user.groups.filter(name='Administrators').exists()

    def has_view_permission(self, request, obj=None):
        # Everyone with admin access can view
        return True

    def get_queryset(self, request):
        # Cache key includes user id to handle different permissions
        cache_key = f'person_admin_list_{request.user.id}'
        cached_qs = cache.get(cache_key)
        
        if cached_qs is not None:
            return cached_qs
        
        # Base queryset with permission filtering
        qs = super().get_queryset(request)
        
        # Filter based on user permissions
        if request.user.is_superuser or request.user.groups.filter(name='Administrators').exists():
            # No filtering needed for admins, but still optimize the query
            qs = qs.select_related('user', 'role').prefetch_related(
                'guardian_relationships', 
                'student_relationships',
                'participation_set__group',  # Corrected: Access groups via participation_set
                'participation_set'
            )
        else:
            # Regular users can only see their own profile
            qs = qs.filter(user=request.user).select_related('user', 'role').prefetch_related(
                'guardian_relationships', 
                'student_relationships',
                'participation_set__group',  # Corrected: Access groups via participation_set
                'participation_set'
            )
        
        # Cache the queryset for 15 minutes
        cache.set(cache_key, qs, 60 * 15)
        
        return qs

    def save_model(self, request, obj, form, change):
        if not change:  # This is a new object
            if not request.user.is_superuser and not request.user.groups.filter(name='Administrators').exists():
                obj.user = request.user  # Force the user to be the current user
        super().save_model(request, obj, form, change)
        
        # Clear caches related to this person
        cache.delete(f'participation_inline_person_{obj.pk}')
        
        # Also clear caches for any groups this person is a member of
        # This is important because person.role affects sorting in ParticipationInline
        for participation in obj.participation_set.all(): # Corrected: Iterate through participations
            if participation.group: # Access group via participation
                cache.delete(f'participation_inline_group_{participation.group.pk}')
        
        # Show generated password if a new user was created via the form
        if hasattr(form, 'generated_password') and form.generated_password:
            messages.success(request, f"User created. The initial password is: {form.generated_password}")


@admin.register(Group)                          
class GroupAdmin(VisibilityModelAdmin):                   
    list_display = ('name', 'visibility_badge', 'get_facilitators', 'description', 'core_competency_1', 'core_competency_2', 'core_competency_3', 'last_modified')
    search_fields = ('name', 'description')
    list_filter = ('is_public', 'core_competency_1', 'core_competency_2', 'core_competency_3')
    filter_horizontal = ('members',)
    inlines = [ParticipationInline]
    
    # Add list_per_page to control pagination in the list view
    list_per_page = 25
    
    # Add actions to help with large datasets
    actions = ['clear_participation_cache', 'rebuild_facilitators_cache']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            # Display participation count in the form
            count_key = f'participation_count_group_{obj.pk}'
            count = cache.get(count_key)
            if count is None:
                count = Participation.objects.filter(group_id=obj.pk).count()
                cache.set(count_key, count, 3600)
                
            if count > 100:
                form.base_fields['participation_warning'] = forms.CharField(
                    required=False,
                    widget=forms.TextInput(attrs={'readonly': 'readonly', 'style': 'border: none; color: #d00;'}),
                    initial=f"Warning: This group has {count} participation records. Performance may be affected.",
                    help_text="Add/edit participations from the individual tab below for better performance."
                )
        return form
    
    def get_queryset(self, request):
        # Cache the queryset for the list view
        cache_key = f'group_admin_list_{request.user.id}'
        cached_qs = cache.get(cache_key)
        
        if cached_qs is not None:
            return cached_qs
        
        # Get base queryset with optimized prefetching
        qs = super().get_queryset(request).prefetch_related(
            'members',
            'core_competency_1', 
            'core_competency_2', 
            'core_competency_3'
        )
        
        # Cache the queryset for 15 minutes
        cache.set(cache_key, qs, 60 * 15)
        return qs
    
    def save_model(self, request, obj, form, change):
        # Call parent method first
        super().save_model(request, obj, form, change)
        # Clear cache for this group
        cache.delete(f'participation_inline_group_{obj.pk}')
        cache.delete(f'group_facilitators_{obj.pk}')
        
        # Clear pagination caches for this group
        for page in range(1, 100):  # Clear a reasonable number of pages
            cache.delete(f'participation_inline_group_{obj.pk}_page{page}')
        
        # Clear the admin list cache for all staff users
        for user in User.objects.filter(is_staff=True):
            cache.delete(f'group_admin_list_{user.id}')
        
    def delete_model(self, request, obj):
        # Clear cache before deletion
        cache.delete(f'participation_inline_group_{obj.pk}')
        cache.delete(f'group_facilitators_{obj.pk}')
        
        # Clear pagination caches for this group
        for page in range(1, 100):  # Clear a reasonable number of pages
            cache.delete(f'participation_inline_group_{obj.pk}_page{page}')
        
        # Clear the admin list cache for all staff users
        for user in User.objects.filter(is_staff=True):
            cache.delete(f'group_admin_list_{user.id}')
        
        super().delete_model(request, obj)
        
    def save_related(self, request, form, formsets, change):
        """Called after saving the related formsets - needed for m2m changes"""
        result = super().save_related(request, form, formsets, change)
        # Clear cache when members change via m2m
        if form.instance.pk:
            cache.delete(f'participation_inline_group_{form.instance.pk}')
            cache.delete(f'group_facilitators_{form.instance.pk}')
            
            # Clear pagination caches for this group
            for page in range(1, 100):  # Clear a reasonable number of pages
                cache.delete(f'participation_inline_group_{form.instance.pk}_page{page}')
            
            # Clear the admin list cache for all staff users
            for user in User.objects.filter(is_staff=True):
                cache.delete(f'group_admin_list_{user.id}')
            
        return result
    
    def clear_participation_cache(self, request, queryset):
        """Action to clear all participation caches for selected groups"""
        count = 0
        for group in queryset:
            cache.delete(f'participation_inline_group_{group.pk}')
            cache.delete(f'group_facilitators_{group.pk}')
            # Clear pagination caches
            for page in range(1, 100):
                cache.delete(f'participation_inline_group_{group.pk}_page{page}')
            count += 1
        self.message_user(request, f"Cleared participation caches for {count} groups")
    clear_participation_cache.short_description = "Clear participation cache for selected groups"
    
    def rebuild_facilitators_cache(self, request, queryset):
        """Action to rebuild facilitator caches for selected groups"""
        count = 0
        for group in queryset:
            # Get facilitator role IDs from cache or DB
            facilitator_ids = cache.get('facilitator_role_ids')
            if facilitator_ids is None:
                facilitator_ids = list(Role.objects.filter(title__iexact='facilitator').values_list('id', flat=True))
                cache.set('facilitator_role_ids', facilitator_ids, 3600)  # Cache for 1 hour
                
            # Find facilitators for this group and cache them    
            facilitators = group.members.filter(role__id__in=facilitator_ids).select_related('user')
            facilitator_names = [f"{p.user.first_name} {p.user.last_name}" for p in facilitators]
            cache.set(f'group_facilitators_{group.pk}', facilitator_names, 86400)  # Cache for 1 day
            count += 1
            
        self.message_user(request, f"Rebuilt facilitator cache for {count} groups")
    rebuild_facilitators_cache.short_description = "Rebuild facilitator cache for selected groups"

    @admin.display(description='Facilitators')
    def get_facilitators(self, obj):
        # Try to get from cache
        facilitator_names = cache.get(f'group_facilitators_{obj.pk}')
        if facilitator_names is not None:
            return ", ".join(facilitator_names) if facilitator_names else "-"
            
        # If not in cache, get facilitator role IDs
        facilitator_ids = cache.get('facilitator_role_ids')
        if facilitator_ids is None:
            facilitator_ids = list(Role.objects.filter(title__iexact='facilitator').values_list('id', flat=True))
            cache.set('facilitator_role_ids', facilitator_ids, 3600)  # Cache for 1 hour
            
        # Get facilitators for this group
        facilitators = obj.members.filter(role__id__in=facilitator_ids).select_related('user')
        facilitator_names = [f"{p.user.first_name} {p.user.last_name}" for p in facilitators]
        
        # Cache for future use
        cache.set(f'group_facilitators_{obj.pk}', facilitator_names, 86400)  # Cache for 1 day
        
        # Return formatted string
        return ", ".join(facilitator_names) if facilitator_names else "-"

    def has_view_permission(self, request, obj=None):
        # Everyone can view all groups
        return True

    def has_change_permission(self, request, obj=None):
        # Superusers and administrators can change any group
        if request.user.is_superuser or request.user.groups.filter(name='Administrators').exists():
            return True
        
        # If this is a specific group, check if user is a facilitator of this group
        if obj:
            # Get facilitator role IDs
            facilitator_ids = cache.get('facilitator_role_ids')
            if facilitator_ids is None:
                facilitator_ids = list(Role.objects.filter(title__iexact='facilitator').values_list('id', flat=True))
                cache.set('facilitator_role_ids', facilitator_ids, 3600)  # Cache for 1 hour
            
            # Check if user is a facilitator in this group
            try:
                person = Person.objects.get(user=request.user)
                if person.role_id in facilitator_ids and person in obj.members.all():
                    return True
            except Person.DoesNotExist:
                pass
                
        return False

    def has_delete_permission(self, request, obj=None):
        # Only superusers and administrators can delete groups
        return request.user.is_superuser or request.user.groups.filter(name='Administrators').exists()


@admin.register(Participation)                
class ParticipationAdmin(VisibilityModelAdmin):
    list_display = ('person', 'group', 'hours', 'special_recognition', 'years_display', 'elementary', 'senior', 'is_public')
    list_filter = ('elementary', 'senior', 'group', 'is_public')
    # visibility actions inherited from VisibilityModelAdmin
    search_fields = ('person__user__username', 'group__name')
    formfield_overrides = {
        models.JSONField: {'widget': YearSelectorWidget()},
    }
    
    def get_queryset(self, request):
        # Cache the queryset for the list view
        cache_key = f'participation_admin_list_{request.user.id}'
        cached_qs = cache.get(cache_key)
        
        if cached_qs is not None:
            return cached_qs
        
        # If not cached, get the queryset with select_related to optimize joins
        qs = super().get_queryset(request).select_related(
            'person', 
            'person__user', 
            'person__role',
            'group'
        )
        
        # Cache the queryset for 15 minutes - will be invalidated when records change
        cache.set(cache_key, qs, 60 * 15)
        return qs
    
    def years_display(self, obj):
        # Cache the formatted years for each participation
        cache_key = f'participation_years_display_{obj.pk}'
        cached_display = cache.get(cache_key)
        
        if cached_display is not None:
            return cached_display
        
        # If not cached, format the years
        display = obj.format_school_years()
        
        # Cache the formatted years for 1 hour
        cache.set(cache_key, display, 60 * 60)
        return display
    years_display.short_description = "School Years"
    
    def save_model(self, request, obj, form, change):
        # Call the parent save_model method first
        super().save_model(request, obj, form, change)
        
        # Clear cache for related Group and Person
        if obj.group:
            cache.delete(f'participation_inline_group_{obj.group.pk}')
        if obj.person:
            cache.delete(f'participation_inline_person_{obj.person.pk}')
            
        # Clear the widget cache for this specific participation
        # This ensures that when a participation's years change, the widget HTML is regenerated
        participation_id = obj.pk
        cache.delete(f'year_widget_html_participation_{participation_id}_*')
        
        # Clear the years display cache
        cache.delete(f'participation_years_display_{obj.pk}')
        
        # Clear the admin list cache for all users
        # This is a bit aggressive, but ensures everyone sees the updated data
        for user in User.objects.filter(is_staff=True):
            cache.delete(f'participation_admin_list_{user.id}')
    
    def delete_model(self, request, obj):
        # Cache clear before deletion to make sure we have the relation info
        if obj.group:
            cache.delete(f'participation_inline_group_{obj.group.pk}')
        if obj.person:
            cache.delete(f'participation_inline_person_{obj.person.pk}')
            
        # Clear the years display cache
        cache.delete(f'participation_years_display_{obj.pk}')
        
        # Clear the admin list cache for all users
        for user in User.objects.filter(is_staff=True):
            cache.delete(f'participation_admin_list_{user.id}')
        
        # Call the parent delete_model method
        super().delete_model(request, obj)

    list_display = ('person', 'group', 'hours', 'special_recognition', 'years_display', 'elementary', 'senior', 'is_public')
    list_filter = ('elementary', 'senior', 'group', 'is_public')
    # visibility actions inherited from VisibilityModelAdmin
    search_fields = ('person__user__username', 'group__name')
    formfield_overrides = {
        models.JSONField: {'widget': YearSelectorWidget()},
    }
    
    def years_display(self, obj):
        return obj.format_school_years()
    years_display.short_description = "School Years"
    

@admin.register(CoreCompetency)
class CoreCompetencyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'description')
    list_filter = ('is_active',)
    search_fields = ('title',)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('group', 'font_choices', 'color_palette', 'logo', 'background_image')
    search_fields = ('group__name',)


@admin.register(Pathways)
class PathwaysAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')


@admin.register(ModelVisibilitySettings)
class ModelVisibilitySettingsAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'access_level', 'last_modified', 'modified_by')
    list_filter = ('access_level',)
    readonly_fields = ('last_modified', 'modified_by')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.modified_by = request.user
        cache.delete(f'model_visibility_{obj.model_name}')  # Clear cache on save

class BadgeZipUploadForm(forms.Form):
    """Form for uploading a zip file containing badge images."""
    zip_file = forms.FileField(
        label="Upload ZIP file containing badge images",
        help_text="The ZIP file should contain PNG images with 512x512 pixel dimensions."
    )

@admin.register(Badges)
class BadgesAdmin(admin.ModelAdmin):
    change_list_template = "admin/badges_changelist.html"
    list_display = ('title', 'description', 'is_active', 'image_tag')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    readonly_fields = ('image_tag',)
    
    def image_tag(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Preview'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-badges/', 
                 self.admin_site.admin_view(self.upload_badges_view), 
                 name='experiences_badges_upload'),
        ]
        return custom_urls + urls
    
    def upload_badges_view(self, request):
        """View to bulk import badges from a ZIP file containing PNGs (non-blocking)."""
        import tempfile
        from .tasks import process_badge_zip
        if request.method == 'POST':
            form = BadgeZipUploadForm(request.POST, request.FILES)
            if form.is_valid():
                zip_file = request.FILES['zip_file']
                # Save the uploaded file to a temp location
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                    for chunk in zip_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                # Always redirect immediately after upload
                reload_url = reverse('admin:experiences_badges_changelist')
                # Use format_html to ensure the link is rendered as HTML
                messages.info(request, format_html(
                    "Badge ZIP upload received. Processing will happen in the background. <a href='{}'>Reload</a> to check for new badges.",
                    reload_url
                ))
                response = HttpResponseRedirect(reload_url)
                # Start background processing (non-blocking, fire-and-forget)
                try:
                    from threading import Thread
                    Thread(target=process_badge_zip, args=(tmp_path, request.user.pk), daemon=True).start()
                except Exception:
                    process_badge_zip(tmp_path, request.user.pk)
                return response
        else:
            form = BadgeZipUploadForm()
        context = {
            'form': form,
            'title': 'Upload Badges from ZIP',
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        return render(request, 'admin/badges_upload.html', context)