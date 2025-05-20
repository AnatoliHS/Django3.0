from django.urls import include, re_path  # Changed import

app_name = "experiences"

urlpatterns = [

    re_path(r'^roles/', include('experiences.urls.role_urls')),  # NOQA
    re_path(r'^people/', include('experiences.urls.person_urls')),
    re_path(r'^activity_groups/', include('experiences.urls.group_urls')),
    re_path(r'^all_activity_participation/', include('experiences.urls.participation_urls')),
    re_path(r'^core_competencies/', include('experiences.urls.core_competency_urls')),
    re_path(r'^themes/', include('experiences.urls.theme_urls')),
    re_path(r'^badges/', include('experiences.urls.badges_urls')),
    re_path(r'^pathways/', include('experiences.urls.pathways_urls')),
]