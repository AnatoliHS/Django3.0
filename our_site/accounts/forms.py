from django import forms
from experiences.models import Person, Group
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from constance import config

class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    group = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        label='Join activity group',
        required=True,
        help_text='Select the group you would like to participate in.'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'group')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the available groups to those that are visible to the public
        self.fields['group'].queryset = Group.objects.filter(is_public=True).order_by('name')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Set user as inactive if pending approval is required
        if config.SIGNUP_NEW_ACCOUNTS_PENDING:
            user.is_active = False
            
        if commit:
            user.save()
        return user

class ProfilePictureForm(forms.ModelForm):
    """Form for updating just the profile picture."""
    
    class Meta:
        model = Person
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].required = False
        
    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Image file too large (maximum 5MB)")
            
            # Check file type
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            file_extension = image.name.split('.')[-1].lower()
            if file_extension not in valid_extensions:
                raise ValidationError(f"Unsupported file type. Allowed types: {', '.join(valid_extensions)}")
                
        return image