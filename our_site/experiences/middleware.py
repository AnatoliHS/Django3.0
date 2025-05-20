from django.http import Http404
from django.core.cache import cache
from .models import ModelVisibilitySettings
import re

class ModelVisibilityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regex patterns for each model URL pattern
        self.model_patterns = {
            'person': r'^/experiences/person/',
            'public_person': r'^/public/person/',
            'group': r'^/experiences/group/',
            'participation': r'^/experiences/participation/',
            'role': r'^/experiences/role/',
            'pathways': r'^/experiences/pathways/',
            'badges': r'^/experiences/badges/',
        }
        self.patterns = {model: re.compile(pattern) 
                        for model, pattern in self.model_patterns.items()}

    def __call__(self, request):
        # Skip admin URLs
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        # Check if URL matches any of our model patterns
        for model_name, pattern in self.patterns.items():
            if pattern.match(request.path):
                # Public person URLs don't require authentication
                if model_name == 'public_person':
                    return self.get_response(request)
                    
                access_level = self.get_access_level(model_name)
                
                if access_level == 'disabled':
                    raise Http404("This section is currently disabled")
                
                if access_level == 'staff' and not request.user.is_staff:
                    raise Http404("Staff access required")
                
                if access_level == 'authenticated' and not request.user.is_authenticated:
                    raise Http404("Login required")
                
                break

        return self.get_response(request)

    def get_access_level(self, model_name):
        """Get the access level for a model, using cache if possible."""
        cache_key = f'model_visibility_{model_name}'
        access_level = cache.get(cache_key)
        
        if access_level is None:
            try:
                setting = ModelVisibilitySettings.objects.get(model_name=model_name)
                access_level = setting.access_level
                cache.set(cache_key, access_level, timeout=3600)  # 1 hour cache
            except ModelVisibilitySettings.DoesNotExist:
                access_level = 'staff'  # Default to staff-only if not configured
                
        return access_level 