from django.urls import re_path  
from ..views import (ThemeListView, ThemeCreateView, ThemeDetailView,
                     ThemeUpdateView, ThemeDeleteView)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    re_path(r'^create/$',  # NOQA
        login_required(ThemeCreateView.as_view()),
        name="theme_create"),

    re_path(r'^(?P<pk>\d+)/update/$',
        login_required(ThemeUpdateView.as_view()),
        name="theme_update"),

    re_path(r'^(?P<pk>\d+)/delete/$',
        login_required(ThemeDeleteView.as_view()),
        name="theme_delete"),

    re_path(r'^(?P<pk>\d+)/$',
        ThemeDetailView.as_view(),
        name="theme_detail"),

    re_path(r'^$',
        ThemeListView.as_view(),
        name="theme_list"),
]
