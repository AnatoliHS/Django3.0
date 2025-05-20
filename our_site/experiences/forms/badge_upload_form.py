from django import forms

class BadgeZipUploadForm(forms.Form):
    """Form for uploading a zip file containing badge images."""
    zip_file = forms.FileField(
        label="Upload ZIP file containing badge images",
        help_text="The ZIP file should contain PNG images with 512x512 pixel dimensions."
    )
