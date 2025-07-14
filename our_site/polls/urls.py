from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("slide/", views.slideshow, name="slideshow"),
    path("test/", views.test, name="test"),
    path("certificate/", views.certificate, name="certificate"),
]