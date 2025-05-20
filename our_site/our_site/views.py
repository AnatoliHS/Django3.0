import json
import random
import subprocess
import os
import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from constance import config
import mimetypes
from django.contrib import admin # Import admin
from django.apps import apps
from django.db import models, transaction
from django.core.exceptions import FieldDoesNotExist
import csv
import traceback # For detailed error logging
from .forms import UploadFileForm # Import the new form

def random_quote_view(request):
    """
    View to select and display a random quote from CONSTANCE_CONFIG QUOTES_LIST.
    """
    # Load the JSON string from Constance
    quotes_json = config.QUOTES_LIST
    try:
        quotes_list = json.loads(quotes_json or '[]')
    except json.JSONDecodeError:
        quotes_list = []

    # Choose a random quote if available
    if quotes_list:
        quote = random.choice(quotes_list)
    else:
        quote = {'text': 'No quotes available.', 'author': ''}

    return render(request, 'quote.html', {'quote': quote})


@staff_member_required
def backup_database(request):
    """
    Creates a JSON dump of the database.
    """
    try:
        # Define backup file path
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        db_backup_filename = f'db_backup_{timestamp}.json'
        db_backup_path = os.path.join(backup_dir, db_backup_filename)

        # Run dumpdata command
        with open(db_backup_path, 'w') as f:
            process = subprocess.run(
                ['python', 'manage.py', 'dumpdata', '--natural-foreign', '--natural-primary', '-e', 'contenttypes', '-e', 'auth.Permission', '--indent', '2'],
                stdout=f,
                stderr=subprocess.PIPE,
                cwd=settings.BASE_DIR, # Run manage.py from the project root
                check=True,
                text=True
            )

        messages.success(request, f'Database successfully backed up to {db_backup_path}')
    except subprocess.CalledProcessError as e:
        messages.error(request, f'Database backup failed: {e.stderr}')
    except Exception as e:
        messages.error(request, f'An error occurred during database backup: {str(e)}')

    return HttpResponseRedirect(reverse('admin:index')) # Redirect back to admin index


@staff_member_required
def backup_management_view(request):
    """
    Admin view to manage backups and restores.
    Lists available backups and provides forms for uploading files for restore.
    """
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    backup_files = []
    if os.path.exists(backup_dir):
        try:
            files = sorted(
                [f for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f))],
                key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)),
                reverse=True
            )
            for filename in files:
                filepath = os.path.join(backup_dir, filename)
                backup_files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                })
        except OSError as e:
            messages.error(request, f"Could not list backup directory: {e}")

    context = {
        'title': 'Backup and Restore Management',
        'backup_files': backup_files,
        'has_permission': request.user.is_staff,
        'csv_form': UploadFileForm(),
        'json_form': UploadFileForm(),
        'media_form': UploadFileForm(),
        **admin.site.each_context(request),
    }
    return render(request, 'admin/backup_restore_management.html', context)

@staff_member_required
def backup_database_flat_csv(request):
    """
    Exploratory function to back up database models to a single flat CSV file.
    This approach flattens all model data into one CSV, which can be very wide
    and sparse. M2M relationships are represented as comma-separated PKs.
    Restoration from such a CSV is complex and not fully implemented here.
    """
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_backup_filename = f'db_flat_backup_{timestamp}.csv'
        csv_backup_path = os.path.join(backup_dir, csv_backup_filename)

        excluded_apps = ['contenttypes', 'admin', 'sessions']
        # dumpdata excludes auth.Permission. Model name is 'permission', app is 'auth'.
        excluded_models_tuples = [('auth', 'permission')]


        models_to_process = []
        all_potential_field_names = set()

        for app_config in apps.get_app_configs():
            if app_config.label.lower() in excluded_apps:
                continue
            for model in app_config.get_models():
                if (app_config.label.lower(), model.__name__.lower()) in excluded_models_tuples:
                    continue
                
                models_to_process.append(model)
                for field in model._meta.get_fields():
                    if not field.concrete:
                        continue
                    if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                        all_potential_field_names.add(f"{field.name}_id")
                    elif isinstance(field, models.ManyToManyField):
                        # For M2M, we'll store a list of related PKs
                        all_potential_field_names.add(f"{field.name}_m2m_pks")
                    else:
                        all_potential_field_names.add(field.name)
        
        # Sort for consistent column order
        sorted_field_names = sorted(list(all_potential_field_names))
        header = ['model_app_label', 'model_name', 'instance_pk'] + sorted_field_names

        with open(csv_backup_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for model in models_to_process:
                model_app = model._meta.app_label
                model_name_str = model._meta.model_name
                queryset = model.objects.all()

                for instance in queryset:
                    row_data = {
                        'model_app_label': model_app,
                        'model_name': model_name_str,
                        'instance_pk': str(instance.pk)
                    }

                    for field_header_name in sorted_field_names:
                        value = '' # Default to empty string for sparse cells
                        try:
                            # Determine actual field name from header_name (e.g., strip _id or _m2m_pks)
                            actual_field_attr_name = field_header_name
                            is_fk_col = field_header_name.endswith('_id') and not field_header_name.endswith('_m2m_pks')
                            is_m2m_col = field_header_name.endswith('_m2m_pks')

                            if is_fk_col:
                                actual_field_attr_name = field_header_name[:-3]
                            elif is_m2m_col:
                                actual_field_attr_name = field_header_name[:-8]

                            field_obj = model._meta.get_field(actual_field_attr_name)

                            if field_obj.name == actual_field_attr_name: # Field exists on this model
                                if is_fk_col and isinstance(field_obj, (models.ForeignKey, models.OneToOneField)):
                                    related_instance = getattr(instance, field_obj.name, None)
                                    if related_instance:
                                        value = str(related_instance.pk)
                                elif is_m2m_col and isinstance(field_obj, models.ManyToManyField):
                                    manager = getattr(instance, field_obj.name)
                                    value = ",".join(str(pk) for pk in manager.values_list('pk', flat=True))
                                elif not is_fk_col and not is_m2m_col: 
                                    if field_header_name == field_obj.name:
                                        attr_value = getattr(instance, field_obj.name, None)
                                        if attr_value is not None:
                                            if isinstance(attr_value, (datetime.date, datetime.datetime)):
                                                value = attr_value.isoformat()
                                            else:
                                                value = str(attr_value)
                        except FieldDoesNotExist:
                            pass 
                        except AttributeError:
                            pass 
                        
                        row_data[field_header_name] = value
                    
                    writer.writerow([row_data.get(col, '') for col in header])
        
        messages.success(request, f'Database (flat CSV exploration) successfully backed up to {csv_backup_path}')

    except Exception as e:
        tb_str = traceback.format_exc()
        messages.error(request, f'An error occurred during flat CSV database backup: {str(e)} \\n{tb_str}')

    return HttpResponseRedirect(reverse('admin:index'))


@staff_member_required
def restore_database_from_flat_csv(request):
    """
    Exploratory function to restore database from a single flat CSV.
    Now includes basic file upload handling.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Uploaded file is not a CSV.')
                return HttpResponseRedirect(reverse('backup_management'))
            
            # Process the CSV file (conceptual placeholder remains)
            # For a real implementation, you would pass csv_file to a processing function.
            # e.g., process_flat_csv_restore(csv_file)
            try:
                # --- BEGINNING OF COMPLEX RESTORE LOGIC (Conceptual) ---
                # This is where you would read csv_file.read().decode('utf-8') (or save to disk and read)
                # and implement the logic described in previous comments.
                # For now, we'll just acknowledge the upload.
                # --- END OF COMPLEX RESTORE LOGIC ---
                messages.warning(request, f"Flat CSV file '{csv_file.name}' received. "
                                          "Restore is a complex operation and is not fully implemented. "
                                          "No data has been changed. This is an exploratory placeholder.")
            except Exception as e:
                messages.error(request, f"Error during conceptual flat CSV restore: {str(e)}")
            
            return HttpResponseRedirect(reverse('backup_management'))
        else:
            messages.error(request, "File upload failed. Please try again.")
            return HttpResponseRedirect(reverse('backup_management'))
    
    # If GET or form invalid, redirect back to management page
    # (though direct GET to this URL isn't typical for restore actions)
    return HttpResponseRedirect(reverse('backup_management'))

@staff_member_required
def backup_media(request):
    """
    Creates a compressed archive of the media directory.
    """
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        media_backup_filename = f'media_backup_{timestamp}.tar.gz'
        media_backup_path = os.path.join(backup_dir, media_backup_filename)
        media_root = settings.MEDIA_ROOT

        if not os.path.isdir(media_root) or not os.listdir(media_root):
             messages.warning(request, f'Media directory ({media_root}) is empty or does not exist. No backup created.')
             return HttpResponseRedirect(reverse('admin:index'))

        # Run tar command to create a compressed archive
        # The command needs to be run from the parent directory of media_root
        parent_dir = os.path.dirname(media_root)
        media_folder_name = os.path.basename(media_root)

        # Ensure the backup path is absolute for the tar command
        absolute_media_backup_path = os.path.abspath(media_backup_path)

        process = subprocess.run(
            ['tar', '-czf', absolute_media_backup_path, '-C', parent_dir, media_folder_name],
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )

        messages.success(request, f'Media files successfully backed up to {media_backup_path}')
    except subprocess.CalledProcessError as e:
        messages.error(request, f'Media backup failed: {e.stderr}')
    except Exception as e:
        messages.error(request, f'An error occurred during media backup: {str(e)}')

    return HttpResponseRedirect(reverse('admin:index')) # Redirect back to admin index

@staff_member_required
def list_backups(request):
    """
    Lists available backup files in the backup directory.
    """
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    backup_files = []
    if os.path.exists(backup_dir):
        try:
            # List files and sort by modification time, newest first
            files = sorted(
                [f for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f))],
                key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)),
                reverse=True
            )
            for filename in files:
                filepath = os.path.join(backup_dir, filename)
                backup_files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                })
        except OSError as e:
            messages.error(request, f"Could not list backup directory: {e}")

    context = {
        'title': 'Available Backups',
        'backup_files': backup_files,
        'has_permission': request.user.is_staff,
        **admin.site.each_context(request), # Include admin context
    }
    return render(request, 'admin/list_backups.html', context)

@staff_member_required
def download_backup(request, filename):
    """
    Serves a specific backup file for download.
    """
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    file_path = os.path.join(backup_dir, filename)

    # Security check: Ensure the requested file is within the backup directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(backup_dir)):
        raise Http404("Invalid file path")

    if os.path.exists(file_path):
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream' # Default if type cannot be guessed
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        raise Http404("File not found")

# Placeholder for restore views - implementation requires careful handling of file uploads and execution order
@staff_member_required
def restore_database(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            backup_file = request.FILES['file']
            if not (backup_file.name.endswith('.json') or backup_file.name.endswith('.json.gz')):
                messages.error(request, "Invalid file type for database restore. Expecting .json or .json.gz")
                return HttpResponseRedirect(reverse('backup_management'))

            # TODO: Implement actual database restore logic using loaddata
            # This involves saving the uploaded file temporarily and then running manage.py loaddata
            # Be very careful with security and file handling here.
            messages.warning(request, f"Database restore from '{backup_file.name}' is not yet fully implemented.")
            return HttpResponseRedirect(reverse('backup_management'))
        else:
            messages.error(request, "File upload failed. Please try again.")
            return HttpResponseRedirect(reverse('backup_management'))
    return HttpResponseRedirect(reverse('backup_management'))

@staff_member_required
def restore_media(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            backup_file = request.FILES['file']
            if not (backup_file.name.endswith('.tar.gz') or backup_file.name.endswith('.zip')):
                messages.error(request, "Invalid file type for media restore. Expecting .tar.gz or .zip")
                return HttpResponseRedirect(reverse('backup_management'))

            # TODO: Implement actual media restore logic (extracting archive to MEDIA_ROOT)
            # This involves saving the uploaded file temporarily and then extracting it.
            # Be very careful with security and file handling here (e.g., path traversal).
            messages.warning(request, f"Media restore from '{backup_file.name}' is not yet fully implemented.")
            return HttpResponseRedirect(reverse('backup_management'))
        else:
            messages.error(request, "File upload failed. Please try again.")
            return HttpResponseRedirect(reverse('backup_management'))
    return HttpResponseRedirect(reverse('backup_management'))

@staff_member_required
def backup_all(request):
    """
    Creates a single backup file containing both the database dump and media files.
    """
    try:
        # Define backup file paths
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create a temp directory for the combined backup
        temp_dir = os.path.join(backup_dir, f'temp_backup_{timestamp}')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 1. Create database dump
        db_backup_filename = 'db_backup.json'
        db_backup_path = os.path.join(temp_dir, db_backup_filename)
        
        with open(db_backup_path, 'w') as f:
            process = subprocess.run(
                ['python', 'manage.py', 'dumpdata', '--natural-foreign', '--natural-primary', 
                 '-e', 'contenttypes', '-e', 'auth.Permission', '--indent', '2'],
                stdout=f,
                stderr=subprocess.PIPE,
                cwd=settings.BASE_DIR,
                check=True,
                text=True
            )
            
        # 2. Copy media files to temp dir
        media_root = settings.MEDIA_ROOT
        if os.path.isdir(media_root) and os.listdir(media_root):
            media_temp_dir = os.path.join(temp_dir, 'media')
            os.makedirs(media_temp_dir, exist_ok=True)
            
            # Use rsync or cp -r to copy media files
            media_folder_name = os.path.basename(media_root)
            process = subprocess.run(
                ['cp', '-r', f"{media_root}/.", media_temp_dir],
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
        
        # 3. Create combined tar archive
        combined_backup_filename = f'full_backup_{timestamp}.tar.gz'
        combined_backup_path = os.path.join(backup_dir, combined_backup_filename)
        
        # Change to the parent directory of temp_dir for the tar command
        temp_dir_parent = os.path.dirname(temp_dir)
        temp_dir_name = os.path.basename(temp_dir)
        
        process = subprocess.run(
            ['tar', '-czf', combined_backup_path, '-C', temp_dir_parent, temp_dir_name],
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        
        # 4. Clean up the temp directory
        subprocess.run(['rm', '-rf', temp_dir])
        
        messages.success(request, f'Full backup (database + media) successfully created at {combined_backup_path}')
    except subprocess.CalledProcessError as e:
        messages.error(request, f'Full backup failed: {e.stderr}')
    except Exception as e:
        messages.error(request, f'An error occurred during full backup: {str(e)}')
        
    return HttpResponseRedirect(reverse('admin:index'))
