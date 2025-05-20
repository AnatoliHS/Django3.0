from django.urls import re_path  
from ..views import (ParticipationListView, ParticipationCreateView, ParticipationDetailView,
                     ParticipationUpdateView, ParticipationDeleteView)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    re_path(r'^create/$',  # NOQA
        login_required(ParticipationCreateView.as_view()),
        name="participation_create"),

    re_path(r'^(?P<pk>\d+)/update/$',
        login_required(ParticipationUpdateView.as_view()),
        name="participation_update"),

    re_path(r'^(?P<pk>\d+)/delete/$',
        login_required(ParticipationDeleteView.as_view()),
        name="participation_delete"),

    re_path(r'^(?P<pk>\d+)/$',
        ParticipationDetailView.as_view(),
        name="participation_detail"),

    re_path(r'^$',
        ParticipationListView.as_view(),
        name="participation_list"),
]
