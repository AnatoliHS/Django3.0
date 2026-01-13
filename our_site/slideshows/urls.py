from django.urls import path
from . import views

app_name = 'slideshows'

urlpatterns = [
    path('save_progress/', views.save_progress, name='save_progress'),
    path('get_progress/', views.get_progress, name='get_progress'),
]
