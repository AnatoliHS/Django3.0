import zipfile
import io
import os
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from .models import Badges

def process_badge_zip(zip_path, uploaded_by):
    """
    Process a zip file at zip_path and create badges in the background.
    """
    created_badges = 0
    skipped_files = 0
    errors = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            file_list = [f for f in z.namelist() if f.lower().endswith('.png') and not f.startswith('__MACOSX/') and not f.endswith('/')]
            for file_name in file_list:
                try:
                    with z.open(file_name) as file_data:
                        img = Image.open(io.BytesIO(file_data.read()))
                        width, height = img.size
                        min_size = int(512 * 0.8)
                        max_size = int(512 * 1.2)
                        if width < min_size or width > max_size or height < min_size or height > max_size:
                            skipped_files += 1
                            continue
                        base_name = os.path.basename(file_name)
                        file_path = os.path.dirname(file_name)
                        if file_path:
                            folder_parts = [part for part in file_path.split('/') if part]
                            if folder_parts:
                                parent_folder = folder_parts[-1]
                                folder_title = parent_folder.replace('_', ' ').replace('-', ' ').title()
                                file_title = os.path.splitext(base_name)[0].replace('_', ' ').replace('-', ' ').title()
                                title = f"{folder_title} - {file_title}"
                            else:
                                title = os.path.splitext(base_name)[0].replace('_', ' ').replace('-', ' ').title()
                        else:
                            title = os.path.splitext(base_name)[0].replace('_', ' ').replace('-', ' ').title()
                        if Badges.objects.filter(title=title).exists():
                            skipped_files += 1
                            continue
                        badge = Badges(title=title, description=f"Badge for {title}")
                        with z.open(file_name) as file_data_again:
                            content = file_data_again.read()
                            badge.image.save(base_name, ContentFile(content), save=False)
                        badge.save()
                        created_badges += 1
                except Exception:
                    skipped_files += 1
    except Exception:
        pass
    # Optionally: send notification to uploaded_by
    return created_badges, skipped_files
