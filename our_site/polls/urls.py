from django.urls import path

from . import views

app_name = 'polls'

urlpatterns = [
    path("", views.index, name="index"),
    path("slide/", views.slideshow, name="slideshow"),
    path("slidePharm/", views.slideshowPharm, name="slideshowPharm"),
    path("slideReg/", views.slideshowReg, name="slideshowReg"),
    path("test/", views.test, name="test"),
    path("certificate/", views.certificate, name="certificate"),
    path('upload_certificate/', views.upload_certificate, name='upload_certificate'),
    path('complete-certificate/', views.complete_certificate, name='complete_certificate'),

]