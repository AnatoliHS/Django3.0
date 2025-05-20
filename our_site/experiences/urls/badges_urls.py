from django.urls import re_path  
from ..views import (BadgesListView, BadgesCreateView, BadgesDetailView,
                     BadgesUpdateView, BadgesDeleteView)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    re_path(r'^create/$',  # NOQA
        login_required(BadgesCreateView.as_view()),
        name="badges_create"),

    re_path(r'^(?P<pk>\d+)/update/$',
        login_required(BadgesUpdateView.as_view()),
        name="badges_update"),

    re_path(r'^(?P<pk>\d+)/delete/$',
        login_required(BadgesDeleteView.as_view()),
        name="badges_delete"),

    re_path(r'^(?P<pk>\d+)/$',
        BadgesDetailView.as_view(),
        name="badges_detail"),

    re_path(r'^$',
        BadgesListView.as_view(),
        name="badges_list"),
]
