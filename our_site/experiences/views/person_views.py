from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from ..models import Person, Participation
from ..forms import PersonForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect # Add redirect import


class PersonListView(ListView):
    model = Person
    template_name = "experiences/person_list.html"
    paginate_by = 20
    context_object_name = "person_list"
    allow_empty = True
    page_kwarg = 'page'
    paginate_orphans = 0

    def __init__(self, **kwargs):
        return super(PersonListView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(PersonListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(PersonListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(PersonListView, self).get_queryset().order_by('graduating_year', 'user__first_name', 'user__last_name')
        
        # If user is not authenticated, don't show any people
        if not self.request.user.is_authenticated:
            return queryset.none()
            
        # Superusers and administrators can see all people
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Administrators').exists():
            return queryset
            
        user_person = None
        try:
            user_person = self.request.user.person
        except Person.DoesNotExist:
            return queryset
            
        # Get IDs of the user's own profile and their students
        person_ids = [user_person.id]
        person_ids.extend(user_person.students.values_list('id', flat=True))
        
        # Return only the user's own profile and their students
        return queryset.filter(id__in=person_ids)

    def get_allow_empty(self):
        return super(PersonListView, self).get_allow_empty()

    def get_context_data(self, *args, **kwargs):
        ret = super(PersonListView, self).get_context_data(*args, **kwargs)
        
        # Add information about which people are the user's students
        if self.request.user.is_authenticated:
            try:
                user_person = self.request.user.person
                students_ids = list(user_person.students.values_list('id', flat=True))
                ret['students_ids'] = students_ids
            except Person.DoesNotExist:
                ret['students_ids'] = []
                
        return ret

    def get_paginate_by(self, queryset):
        return super(PersonListView, self).get_paginate_by(queryset)

    def get_context_object_name(self, object_list):
        return super(PersonListView, self).get_context_object_name(object_list)

    def paginate_queryset(self, queryset, page_size):
        return super(PersonListView, self).paginate_queryset(queryset, page_size)

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return super(PersonListView, self).get_paginator(queryset, per_page, orphans=0, allow_empty_first_page=True)

    def render_to_response(self, context, **response_kwargs):
        return super(PersonListView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PersonListView, self).get_template_names()


class PersonDetailView(DetailView):
    model = Person
    template_name = "experiences/person_detail.html"
    context_object_name = "person"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def __init__(self, **kwargs):
        return super(PersonDetailView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(PersonDetailView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(PersonDetailView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user

        # Allow access if the profile is public
        if obj.is_public:
            return obj

        # If not public, check if user is authenticated
        if not user.is_authenticated:
            # Instead of raising PermissionDenied immediately, 
            # Let's raise PermissionDenied for now, assuming login is required for non-public.
            raise PermissionDenied("Please log in to view this private profile.")
        
        # If authenticated, check specific permissions for private profiles
        # Superusers and administrators can view all profiles
        if user.is_superuser or user.groups.filter(name='Administrators').exists():
            return obj

        # Users can view their own profile
        if hasattr(user, 'person') and obj == user.person:
             return obj

        # Guardians can view their students' profiles
        if hasattr(user, 'person') and user.person.students.filter(id=obj.id).exists():
            return obj

        # Students can view their guardians' profiles
        if hasattr(user, 'person') and user.person.guardians.filter(id=obj.id).exists():
            return obj

        # If none of the conditions are met, deny access
        raise PermissionDenied("You don't have permission to view this private profile.")

    def get_queryset(self):
        return super(PersonDetailView, self).get_queryset()

    def get_slug_field(self):
        return super(PersonDetailView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        person = self.object # person whose profile is being viewed
        viewer_person = getattr(user, 'person', None) # person viewing the profile, if they have one

        # Determine if the current user can edit this profile
        can_edit = (
            user.is_authenticated and (
                user.is_superuser or
                user.groups.filter(name='Administrators').exists() or
                person == viewer_person
            )
        )
        context['can_edit'] = can_edit

        # Simplified visibility: owner/admin sees all, otherwise respect public flags
        is_owner = person == viewer_person
        is_admin = user.is_authenticated and (user.is_superuser or user.groups.filter(name='Administrators').exists())

        # Guardians visibility
        if is_admin or is_owner:
            guardian_qs = person.student_relationships.filter(is_active=True)
        elif person.is_public and person.show_guardians_publicly:
            guardian_qs = person.student_relationships.filter(is_active=True)
        else:
            guardian_qs = person.student_relationships.none()
        context['show_guardians'] = guardian_qs.exists()
        context['guardian_relationships'] = guardian_qs

        # Students visibility (only for owner/admin)
        student_qs = person.guardian_relationships.filter(is_active=True) if (is_admin or is_owner) else person.guardian_relationships.none()
        context['show_students'] = student_qs.exists()
        context['student_relationships'] = student_qs

        # Activities visibility
        if is_admin or is_owner:
            participation_qs = person.participation_set.all()
        elif person.is_public and person.show_activities_publicly:
            participation_qs = person.participation_set.all()
        else:
            participation_qs = person.participation_set.none()
        context['show_activities'] = participation_qs.exists()
        context['participations'] = participation_qs

        # Retain public flag for template
        context['is_public_profile'] = person.is_public
        return context

    def get_context_object_name(self, obj):
        return super(PersonDetailView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(PersonDetailView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PersonDetailView, self).get_template_names()


class PersonCreateView(CreateView):
    model = Person
    form_class = PersonForm
    # fields = ['user', 'profile_picture', 'role']
    template_name = "experiences/person_create.html"
    success_url = reverse_lazy("person_list")

    def __init__(self, **kwargs):
        return super(PersonCreateView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super(PersonCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(PersonCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(PersonCreateView, self).post(request, *args, **kwargs)

    def get_form_class(self):
        return super(PersonCreateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(PersonCreateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(PersonCreateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(PersonCreateView, self).get_initial()

    def form_invalid(self, form):
        return super(PersonCreateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(PersonCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PersonCreateView, self).get_context_data(**kwargs)
        return ret

    def render_to_response(self, context, **response_kwargs):
        return super(PersonCreateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PersonCreateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:person_detail", args=(self.object.pk,))


class PersonUpdateView(UpdateView):
    model = Person
    form_class = PersonForm
    # fields = ['user', 'profile_picture', 'role']
    template_name = "experiences/person_update.html"
    initial = {}
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "person"

    def __init__(self, **kwargs):
        return super(PersonUpdateView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(PersonUpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(PersonUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(PersonUpdateView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(PersonUpdateView, self).get_object(queryset)

    def get_queryset(self):
        return super(PersonUpdateView, self).get_queryset()

    def get_slug_field(self):
        return super(PersonUpdateView, self).get_slug_field()

    def get_form_class(self):
        return super(PersonUpdateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(PersonUpdateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(PersonUpdateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(PersonUpdateView, self).get_initial()

    def form_invalid(self, form):
        return super(PersonUpdateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(PersonUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PersonUpdateView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(PersonUpdateView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(PersonUpdateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PersonUpdateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:person_detail", args=(self.object.pk,))


class PersonDeleteView(DeleteView):
    model = Person
    template_name = "experiences/person_delete.html"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "person"

    def __init__(self, **kwargs):
        return super(PersonDeleteView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(PersonDeleteView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        return super(PersonDeleteView, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(PersonDeleteView, self).delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(PersonDeleteView, self).get_object(queryset)

    def get_queryset(self):
        return super(PersonDeleteView, self).get_queryset()

    def get_slug_field(self):
        return super(PersonDeleteView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(PersonDeleteView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(PersonDeleteView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(PersonDeleteView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PersonDeleteView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:person_list")
