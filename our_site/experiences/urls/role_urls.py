from django.urls import re_path  
from ..views import (RoleListView, RoleCreateView, RoleDetailView,
                     RoleUpdateView, RoleDeleteView)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    re_path(r'^create/$',  # NOQA
        login_required(RoleCreateView.as_view()),
        name="role_create"),

    re_path(r'^(?P<pk>\d+)/update/$',
        login_required(RoleUpdateView.as_view()),
        name="role_update"),

    re_path(r'^(?P<pk>\d+)/delete/$',
        login_required(RoleDeleteView.as_view()),
        name="role_delete"),

    re_path(r'^(?P<pk>\d+)/$',
        RoleDetailView.as_view(),
        name="role_detail"),

    re_path(r'^$',
        RoleListView.as_view(),
        name="role_list"),
]
