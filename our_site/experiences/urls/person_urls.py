from django.urls import re_path  
from ..views import (PersonListView, PersonCreateView, PersonDetailView,
                     PersonUpdateView, PersonDeleteView)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    re_path(r'^create/$',  # NOQA
        login_required(PersonCreateView.as_view()),
        name="person_create"),

    re_path(r'^(?P<pk>\d+)/update/$',
        login_required(PersonUpdateView.as_view()),
        name="person_update"),

    re_path(r'^(?P<pk>\d+)/delete/$',
        login_required(PersonDeleteView.as_view()),
        name="person_delete"),

    re_path(r'^(?P<pk>\d+)/$',
        PersonDetailView.as_view(),
        name="person_detail"),

    re_path(r'^$',
        PersonListView.as_view(),
        name="person_list"),
]
