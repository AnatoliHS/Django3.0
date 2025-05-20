from django.urls import path

from . import views

app_name = 'experiences'

urlpatterns = [
    path("", views.index, name="index"),
    path('person/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('person/<slug:slug>/', views.PersonDetailView.as_view(), name='person_detail'),
]