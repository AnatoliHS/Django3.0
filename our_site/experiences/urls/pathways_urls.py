from django.urls import re_path  
from ..views import (PathwaysListView, PathwaysCreateView, PathwaysDetailView,
                     PathwaysUpdateView, PathwaysDeleteView)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    re_path(r'^create/$',  # NOQA
        login_required(PathwaysCreateView.as_view()),
        name="pathways_create"),

    re_path(r'^(?P<pk>\d+)/update/$',
        login_required(PathwaysUpdateView.as_view()),
        name="pathways_update"),

    re_path(r'^(?P<pk>\d+)/delete/$',
        login_required(PathwaysDeleteView.as_view()),
        name="pathways_delete"),

    re_path(r'^(?P<pk>\d+)/$',
        PathwaysDetailView.as_view(),
        name="pathways_detail"),

    re_path(r'^$',
        PathwaysListView.as_view(),
        name="pathways_list"),
]
