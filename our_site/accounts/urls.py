from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.AccountDashboardView.as_view(), name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/create/', views.create_profile_view, name='create_profile'),
    path('register/', views.register_view, name='register'),
    path('confirm-email/<uidb64>/<token>/', views.confirm_email_view, name='confirm_email'),
    path('update-visibility/', views.update_visibility, name='update_visibility'),
    path('toggle-participation/<int:pk>/', views.toggle_participation_visibility, name='toggle_participation_visibility'),
]