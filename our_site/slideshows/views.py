from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import SlideshowProgress
import json
from django.views.decorators.csrf import ensure_csrf_cookie

@login_required
@require_POST
def save_progress(request):
    try:
        data = json.loads(request.body)
        slideshow_slug = data.get('slideshow_slug')
        current_h = data.get('current_h', 0)
        current_v = data.get('current_v', 0)
        max_percentage = data.get('max_percentage', 0)
        
        # Ensure they are integers (handle None explicitly if key existed but value was null)
        if current_h is None: current_h = 0
        if current_v is None: current_v = 0
        if max_percentage is None: max_percentage = 0
        
        if not slideshow_slug:
             return JsonResponse({'status': 'error', 'message': 'Missing slideshow_slug'}, status=400)

        progress, created = SlideshowProgress.objects.get_or_create(
            user=request.user,
            slideshow_slug=slideshow_slug
        )
        
        progress.current_h = current_h
        progress.current_v = current_v
        
        # Only update max_percentage if it's greater than before
        if max_percentage > progress.max_percentage:
            progress.max_percentage = max_percentage
            
        progress.save()
        
        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_GET
def get_progress(request):
    slideshow_slug = request.GET.get('slideshow_slug')
    
    if not slideshow_slug:
        return JsonResponse({'status': 'error', 'message': 'Missing slideshow_slug'}, status=400)
        
    try:
        progress = SlideshowProgress.objects.get(user=request.user, slideshow_slug=slideshow_slug)
        return JsonResponse({
            'status': 'success',
            'current_h': progress.current_h,
            'current_v': progress.current_v,
            'max_percentage': progress.max_percentage,
            'completed': progress.completed
        })
    except SlideshowProgress.DoesNotExist:
        return JsonResponse({
            'status': 'success',
            'current_h': 0,
            'current_v': 0,
            'max_percentage': 0,
            'completed': False
        })
