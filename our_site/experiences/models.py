from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import admin
from django.utils.html import format_html
from django.db.models.signals import post_save
from django.dispatch import receiver



class BaseVisibilityModel(models.Model):
    is_public = models.BooleanField(
        default=True,
        help_text="Controls whether this item is visible to the public"
    )
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Role(BaseVisibilityModel):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Person(BaseVisibilityModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='media/profile_pictures/', null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='people')
    graduating_year = models.IntegerField(null=True, blank=True)
    guardians = models.ManyToManyField('self', through='GuardianStudent', 
                                     symmetrical=False,
                                     through_fields=('student', 'guardian'),
                                     related_name='students')
    show_activities_publicly = models.BooleanField(default=False, help_text="Whether to show activities on public profile")
    show_guardians_publicly = models.BooleanField(default=False, help_text="Whether to show guardians on public profile")
    cached_str = models.CharField(max_length=255, blank=True, editable=False, 
                                help_text="Cached string representation of this person")

    def __str__(self):
        if not self.cached_str:
            self.update_cached_str()
        return self.cached_str

    def update_cached_str(self):
        name = self.user.get_full_name() or self.user.username
        role_str = self.role.title if self.role else 'No Role'
        grad_year_str = f", Graduating: {self.graduating_year}" if self.graduating_year else ""
        self.cached_str = f"{name} ({role_str}{grad_year_str})"
        # Save without triggering save signals to avoid recursion
        Person.objects.filter(pk=self.pk).update(cached_str=self.cached_str)

    def is_active(self):
        """Returns True if the user is active based on their last login time."""
        return self.user.last_login >= timezone.now() - timezone.timedelta(days=30)

    @admin.display(description="Participation Details")
    def get_participations(self):
        """Returns a string representation of all participations."""
        participations = Participation.objects.filter(person=self)
        return ", ".join([f"{p.group.name} ({p.format_school_years()})" for p in participations])

    class Meta:
        verbose_name_plural = "People"

class GuardianStudent(models.Model):
    guardian = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='guardian_relationships')
    student = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='student_relationships')
    relationship = models.CharField(max_length=50, help_text="e.g., Parent, Legal Guardian, Grandparent")
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="Whether this relationship is currently active")
    notes = models.TextField(blank=True, help_text="Any additional notes about this relationship")

    class Meta:
        verbose_name = "Guardian-Student Relationship"
        verbose_name_plural = "Guardian-Student Relationships"
        unique_together = ('guardian', 'student')
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.guardian} is {self.relationship} of {self.student}"

class Group(BaseVisibilityModel):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField('Person', through='Participation')
    description = models.TextField(blank=True)
    badges = models.ForeignKey('Badges' , on_delete=models.SET_NULL, null=True, blank=True, related_name='groups',
                                  help_text="Badges displayed for this group")
    core_competency_1 = models.ForeignKey('CoreCompetency', on_delete=models.SET_NULL, null=True, blank=True, related_name='group_core_1')
    core_competency_2 = models.ForeignKey('CoreCompetency', on_delete=models.SET_NULL, null=True, blank=True, related_name='group_core_2')
    core_competency_3 = models.ForeignKey('CoreCompetency', on_delete=models.SET_NULL, null=True, blank=True, related_name='group_core_3')

    class Meta:
        verbose_name_plural = "Activity Groups"

    def __str__(self):
        return self.name


class Participation(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    hours = models.PositiveIntegerField(null=True, blank=True)  # Hours of participation
    special_recognition = models.TextField(blank=True, null=True)  # Optional special recognition
    years = models.JSONField(default=list)  # List of years they participated
    elementary = models.BooleanField(default=False)  # Elementary level participation
    senior = models.BooleanField(default=False)  # Senior senior school level participation
    is_public = models.BooleanField(default=False, help_text="Whether this participation is visible on public profiles")
    badges = models.ForeignKey('Badges' , on_delete=models.SET_NULL, null=True, blank=True, related_name='participations',
                                  help_text="Badge awarded for this specific participation")

    class Meta:
        verbose_name_plural = "All Activity Participation"

    def format_school_years(self):
        """Format years as school years (YYYY-YYYY+1) in chronological order."""
        sorted_years = sorted(self.years)
        return ", ".join([f"{year}-{year+1}" for year in sorted_years])

    def __str__(self):
        return f"{self.person} in {self.group} ({self.format_school_years()})"


class CoreCompetency(models.Model):
    title = models.CharField(max_length=100, unique=True)  # Unique title for the competency
    description = models.TextField(blank=True)  # Optional description
    is_active = models.BooleanField(default=True)  # Whether the competency is active

    class Meta:
        verbose_name_plural = "Core Competencies"

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"


class Theme(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)  # Connects each theme to a group
    color_palette = models.JSONField()  # Stores color values
    font_choices = models.CharField(max_length=100)  # Specify the font choice
    logo = models.ImageField(upload_to='media/logos/', null=True, blank=True)
    background_image = models.ImageField(upload_to='media/backgrounds/', null=True, blank=True)

    def __str__(self):
        return f"Theme for {self.group.name}"


class Pathways(models.Model):
    title = models.CharField(max_length=100, unique=True)  # Unique title for the pathway
    description = models.TextField(blank=True)  # Optional description
    core_competencies = models.ManyToManyField(CoreCompetency)  # Connects to core competencies
    groups = models.ManyToManyField(Group)  # Connects to groups
    is_active = models.BooleanField(default=True)  # Whether the pathway is active

    class Meta:
        verbose_name_plural = "Pathways"

    def __str__(self):
        return self.title

    def long_title(self):
        return f"{self.title} (is made of {', '.join(map(str, self.core_competencies.all()))})"

class Badges(models.Model):
    title = models.CharField(max_length=100, unique=True)  # Unique title for the badge
    description = models.TextField(blank=True)  # Optional description
    image = models.ImageField(upload_to='media/badges/', null=True, blank=True)
    core_competencies = models.ManyToManyField(CoreCompetency, blank=True)  # Connects to core competencies
    is_active = models.BooleanField(default=True)  # Whether the badge is active

    class Meta:
        verbose_name_plural = "Badges"

    def __str__(self):
        return self.title

    def image_tag(self):
        if self.image:
            return format_html('<img src="{}" width="50" height="50" />', self.image.url)
        return "No Image"

class ModelVisibilitySettings(models.Model):
    MODEL_CHOICES = [
        ('person', 'People'),
        ('group', 'Activity Groups'),
        ('participation', 'Participations'),
        ('role', 'Roles'),
        ('pathways', 'Pathways'),
        ('badges', 'Badges'),
    ]

    ACCESS_LEVELS = [
        ('public', 'Public - Anyone can view'),
        ('authenticated', 'Authenticated - Any logged in user'),
        ('staff', 'Staff Only'),
        ('disabled', 'Disabled - No access (404)'),
    ]

    model_name = models.CharField(
        max_length=50, 
        choices=MODEL_CHOICES,
        unique=True,
        help_text="Select which model's visibility to control"
    )
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVELS,
        default='staff',
        help_text="Who can access this model's views"
    )
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Model Visibility Setting"
        verbose_name_plural = "Model Visibility Settings"
        ordering = ['model_name']

    def __str__(self):
        return f"{self.get_model_name_display()} - {self.get_access_level_display()}"

# Signal handlers for Person model caching
@receiver(post_save, sender=User)
def update_person_cache_on_user_change(sender, instance, **kwargs):
    """Update the cached string representation when the User object changes"""
    try:
        if hasattr(instance, 'person'):
            instance.person.update_cached_str()
    except Exception:
        # Handle case where Person might not exist yet
        pass

@receiver(post_save, sender=Role)
def update_persons_cache_on_role_change(sender, instance, **kwargs):
    """Update the cached string for all persons with this role when the Role changes"""
    for person in instance.people.all():
        person.update_cached_str()

@receiver(post_save, sender=Person)
def update_person_cache(sender, instance, created, **kwargs):
    """Update the cached string representation when the Person object changes"""
    if created or not instance.cached_str:
        instance.update_cached_str()

