from django import forms
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.core.cache import cache
import datetime
import json

class YearSelectorWidget(forms.Widget):
    """
    A custom widget that displays a list of checkboxes for year selection.
    Converts between a JSON list of years and a user-friendly checkbox interface.
    """
    template_name = 'admin/widgets/year_selector.html'

    def __init__(self, attrs=None, year_range=None):
        super().__init__(attrs)
        self.year_range = year_range or 5  # Default to showing 5 years in the long run it should be 12 years for a k-12 school

    def format_school_year(self, year):
        """Format a year as a school year (YYYY-YYYY+1)"""
        return f"{year}-{year+1}"
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        # Convert value from JSON list [2020, 2024, 2025] to a list of years if it exists
        current_years = set()
        if value:
            if isinstance(value, list):
                current_years = set(value)
            else:
                try:
                    # Handle case when it might come in as a string
                    current_years = set(json.loads(value))
                except (TypeError, json.JSONDecodeError):
                    current_years = set()
        
        # Try to get year choices from cache
        cache_key = 'year_selector_choices'
        year_choices = cache.get(cache_key)
        
        if year_choices is None:
            # Generate a range of years to show
            current_year = datetime.datetime.now().year
            years = list(range(current_year - self.year_range, current_year + 1))
            
            year_choices = []
            for year in sorted(years, reverse=True):  # Show newest years first
                year_choices.append({
                    'year': year,
                    'school_year': self.format_school_year(year),
                })
            
            # Cache the year choices - this rarely changes (only once per year)
            cache.set(cache_key, year_choices, 60 * 60 * 24 * 30)  # Cache for 30 days
        
        # Mark selected years
        context_year_choices = []
        for choice in year_choices:
            context_year_choices.append({
                'year': choice['year'],
                'school_year': choice['school_year'],
                'checked': choice['year'] in current_years,
            })
        
        context['widget']['year_choices'] = context_year_choices
        return context
    
    def render(self, name, value, attrs=None, renderer=None):
        # Generate a cache key for the rendered widget
        # Since each widget's HTML depends on its name and selected years,
        # we need to include those in the cache key
        value_str = str(value) if value else ""
        
        # Check if this is a widget for a specific participation instance
        # Extract participation ID from name if possible (e.g., "id_participation_set-0-years")
        participation_id = None
        if name.startswith('id_participation_set-'):
            parts = name.split('-')
            if len(parts) >= 3 and parts[2].isdigit():
                participation_id = parts[2]
        
        # Include participation ID in cache key if available for more granular caching
        if participation_id:
            cache_key = f'year_widget_html_participation_{participation_id}_{hash(value_str)}'
        else:
            cache_key = f'year_widget_html_{name}_{hash(value_str)}'
        
        # Try to get cached HTML
        cached_html = cache.get(cache_key)
        if cached_html is not None:
            return mark_safe(cached_html)
        
        # Generate HTML if not in cache
        context = self.get_context(name, value, attrs)
        
        # Create HTML directly since we don't have a template
        html = '<div class="year-selector">'
        html += f'<input type="hidden" name="{name}" id="id_{name}" value="">'
        html += '<div style="display: flex; flex-wrap: wrap; gap: 8px; max-width: 600px;">'
        
        for choice in context['widget']['year_choices']:
            checked = 'checked' if choice['checked'] else ''
            year = choice['year']
            school_year = choice['school_year']
            
            html += f'''
            <div style="flex: 0 0 120px;">
                <label style="display: flex; align-items: center;">
                    <input type="checkbox" name="{name}_year" value="{year}" {checked}
                           onchange="updateYearValues('{name}')">
                    <span style="margin-left: 5px;">{school_year}</span>
                </label>
            </div>
            '''
        
        html += '</div>'
        html += f'''
        <script>
        function updateYearValues(fieldName) {{
            const checkboxes = document.querySelectorAll(`input[name="${{fieldName}}_year"]:checked`);
            const years = Array.from(checkboxes).map(cb => parseInt(cb.value));
            document.getElementById(`id_${{fieldName}}`).value = JSON.stringify(years);
        }}
        // Initialize the value when the page loads
        document.addEventListener('DOMContentLoaded', function() {{
            updateYearValues('{name}');
        }});
        </script>
        '''
        html += '</div>'
        
        # Cache the rendered HTML for 1 day
        # Use longer cache time for participation-specific widgets
        cache_timeout = 60 * 60 * 24 * 7 if participation_id else 60 * 60 * 24
        cache.set(cache_key, html, cache_timeout)
        
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        # Extract the year values from checkboxes and return as a list
        year_values = data.getlist(f"{name}_year")
        if not year_values:
            return json.dumps([])  # Return empty JSON array as string
        
        # Convert to JSON string instead of Python list
        return json.dumps([int(year) for year in year_values])