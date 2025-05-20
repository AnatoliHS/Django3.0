"""
URL configuration for our_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django_startr.views import debug_index, debug_permission_denied
from accounts.views import register_view, toggle_participation_visibility  # Add this import at top
# Import backup/restore views
from .views import (
    random_quote_view, backup_database, backup_media, 
    restore_database, restore_media, list_backups, download_backup,
    backup_all,  # Add the new backup_all view
    backup_database_flat_csv, restore_database_from_flat_csv, # Add CSV views
    backup_management_view # Add the new management view
)

# Custom view for the root URL
from django.shortcuts import render

def home_view(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        # Use the login template with a welcome message
        return LoginView.as_view(template_name='registration/login.html', 
                                extra_context={
                                    'title': 'Particip8',
                                    'welcome_message': 'Where participation becomes portfolio'
                                    })(request)

# Define backup/restore URL patterns
backup_urlpatterns = [
    path('backup/database/', backup_database, name='backup_database'),
    path('backup/media/', backup_media, name='backup_media'),
    path('backup/all/', backup_all, name='backup_all'),
    path('backup/database/csv/', backup_database_flat_csv, name='backup_database_flat_csv'),
    path('restore/database/', restore_database, name='restore_database'),
    path('restore/media/', restore_media, name='restore_media'),
    path('restore/database/csv/', restore_database_from_flat_csv, name='restore_database_from_flat_csv'),
    path('backups/download/<path:filename>', download_backup, name='download_backup'),
    path('', backup_management_view, name='backup_management'), # Add the main management view URL
]

urlpatterns = [
    # Direct toggle route for participation visibility
    path('accounts/toggle-participation/<int:pk>/', toggle_participation_visibility, name='toggle_participation_visibility'),
    path('', home_view, name='home'),
    path('quote/', random_quote_view, name='random_quote'),
    path("experiences/", include("experiences.urls")),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('auth/', include('django.contrib.auth.urls')),
    # Include backup/restore URLs under the admin path
    path("admin/", include(backup_urlpatterns)),
    path("admin/", admin.site.urls), # Keep the standard admin URLs
    path('register/', register_view, name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add Django Debug Toolbar URL patterns if in DEBUG mode
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]


handler404 = 'django_startr.views.debug_index'
handler403 = 'django_startr.views.debug_permission_denied'

urlpatterns += [
        # Only allow the home page and authentication URLs to be accessed without login
        re_path(r'^$', home_view),
        re_path(r'^auth/.*$', include('django.contrib.auth.urls')),
        re_path(r'^register/$', register_view),  # Allow access to registration
        re_path(r'^admin/.*$', admin.site.urls),
        # Lets temporarily allow access to peop
        re_path(r'^experiences/profile/', include('experiences.urls.person_urls')),
        # All other paths require login
        re_path(r'^.*$', login_required(debug_index)),
    ]

admin.site.site_header = "Startr Admin"
admin.site.site_title = "Startr Education Admin Portal"
admin.site.index_title = "Welcome to your Startr Education admin panel"

