from django.contrib import admin
from django.utils.html import format_html
from .models import *
from django import forms
from django.shortcuts import render
from django.urls import path, reverse
from django.contrib import messages
from PIL import Image
from django.core.files.base import ContentFile
from io import TextIOWrapper, StringIO
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Case, When, Value, IntegerField
from .admin_widgets import YearSelectorWidget
from .forms import PersonForm
import json
import random
import string
import zipfile
import tempfile
import io
import os


@admin.register(Group)                          
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_facilitators', 'description', 'core_competency_1', 'core_competency_2', 'core_competency_3', 'last_modified')
    search_fields = ('name', 'description')
    list_filter = ('is_public', 'core_competency_1', 'core_competency_2', 'core_competency_3')
    filter_horizontal = ('members',)
    
    @admin.display(description='Facilitators')
    def get_facilitators(self, obj):
        # Get the current school year (runs from Sept to Aug, so if it's 2025 now, the school year is 2024-2025)
        from django.utils import timezone
        current_date = timezone.now()
        current_year = current_date.year
        # If we're before September, we're in the previous school year
        if current_date.month < 9:
            school_year = current_year - 1
        else:
            school_year = current_year
            
        # Find all facilitators for this group - no caching, just direct query
        # Use prefetch_related to optimize the query
        facilitators = Person.objects.filter(
            groups=obj,
            role__title__iexact='facilitator'  # Case-insensitive match
        ).select_related('user').distinct()
        
        # Filter for the current school year
        filtered_facilitators = []
        for facilitator in facilitators:
            # Get participations for this facilitator in this group
            participations = Participation.objects.filter(person=facilitator, group=obj)
            
            # Check each participation for the current school year
            for participation in participations:
                years = []
                if participation.years:
                    try:
                        years = json.loads(participation.years)
                    except (json.JSONDecodeError, TypeError):
                        continue
                        
                if school_year in years:
                    filtered_facilitators.append(facilitator)
                    break
        
        # Return the formatted list of facilitators
        if filtered_facilitators:
            return ", ".join([f.user.get_full_name() or f.user.username for f in filtered_facilitators])
        else:
            return "-"
