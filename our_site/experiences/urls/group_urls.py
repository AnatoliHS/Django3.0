from django.urls import re_path  
from ..views import (GroupListView, GroupCreateView, GroupDetailView,
                     GroupUpdateView, GroupDeleteView)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    re_path(r'^create/$',  # NOQA
        login_required(GroupCreateView.as_view()),
        name="group_create"),

    re_path(r'^(?P<pk>\d+)/update/$',
        login_required(GroupUpdateView.as_view()),
        name="group_update"),

    re_path(r'^(?P<pk>\d+)/delete/$',
        login_required(GroupDeleteView.as_view()),
        name="group_delete"),

    re_path(r'^(?P<pk>\d+)/$',
        GroupDetailView.as_view(),
        name="group_detail"),

    re_path(r'^$',
        GroupListView.as_view(),
        name="group_list"),
]
