from django.urls import re_path  
from ..views import (CoreCompetencyListView, CoreCompetencyCreateView, CoreCompetencyDetailView,
                     CoreCompetencyUpdateView, CoreCompetencyDeleteView)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    re_path(r'^create/$',  # NOQA
        login_required(CoreCompetencyCreateView.as_view()),
        name="core_competency_create"),

    re_path(r'^(?P<pk>\d+)/update/$',
        login_required(CoreCompetencyUpdateView.as_view()),
        name="core_competency_update"),

    re_path(r'^(?P<pk>\d+)/delete/$',
        login_required(CoreCompetencyDeleteView.as_view()),
        name="core_competency_delete"),

    re_path(r'^(?P<pk>\d+)/$',
        CoreCompetencyDetailView.as_view(),
        name="core_competency_detail"),

    re_path(r'^$',
        CoreCompetencyListView.as_view(),
        name="core_competency_list"),
]
