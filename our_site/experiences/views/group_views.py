from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from ..models import Group
from ..forms import GroupForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import Http404
from django.core.exceptions import PermissionDenied


class GroupListView(ListView):
    model = Group
    template_name = "experiences/group_list.html"
    paginate_by = 20
    context_object_name = "group_list"
    allow_empty = True
    page_kwarg = 'page'
    paginate_orphans = 0

    def __init__(self, **kwargs):
        return super(GroupListView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(GroupListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(GroupListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        # Everyone can see all groups
        return super().get_queryset().order_by('name')

    def get_allow_empty(self):
        return super(GroupListView, self).get_allow_empty()

    def get_context_data(self, *args, **kwargs):
        ret = super(GroupListView, self).get_context_data(*args, **kwargs)
        return ret

    def get_paginate_by(self, queryset):
        return super(GroupListView, self).get_paginate_by(queryset)

    def get_context_object_name(self, object_list):
        return super(GroupListView, self).get_context_object_name(object_list)

    def paginate_queryset(self, queryset, page_size):
        return super(GroupListView, self).paginate_queryset(queryset, page_size)

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return super(GroupListView, self).get_paginator(queryset, per_page, orphans=0, allow_empty_first_page=True)

    def render_to_response(self, context, **response_kwargs):
        return super(GroupListView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(GroupListView, self).get_template_names()


class GroupDetailView(DetailView):
    model = Group
    template_name = "experiences/group_detail.html"
    context_object_name = "group"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def __init__(self, **kwargs):
        return super(GroupDetailView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(GroupDetailView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(GroupDetailView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(GroupDetailView, self).get_object(queryset)

    def get_queryset(self):
        return super(GroupDetailView, self).get_queryset()

    def get_slug_field(self):
        return super(GroupDetailView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        group = self.object
        
        # Filter members based on user permissions
        if user.is_superuser or user.groups.filter(name='Administrators').exists() or user.is_staff:
            # Staff, superusers, and administrators can see all members
            context['visible_members'] = group.members.all()
        else:
            try:
                person = user.person
                # Get IDs of the user and their children/students
                visible_person_ids = [person.id]
                visible_person_ids.extend(person.students.values_list('id', flat=True))
                
                # Only show members who are the user themselves or their children
                context['visible_members'] = group.members.filter(id__in=visible_person_ids)
                
                # Add a flag to indicate filtering is in place
                context['members_filtered'] = True
            except:
                # If user doesn't have a person profile, show no members
                context['visible_members'] = group.members.none()
                context['members_filtered'] = True
        
        return context

    def get_context_object_name(self, obj):
        return super(GroupDetailView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(GroupDetailView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(GroupDetailView, self).get_template_names()


class GroupCreateView(CreateView):
    model = Group
    form_class = GroupForm
    # fields = ['name', 'description', 'core_competency_1', 'core_competency_2', 'core_competency_3']
    template_name = "experiences/group_create.html"
    success_url = reverse_lazy("group_list")

    def __init__(self, **kwargs):
        return super(GroupCreateView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super(GroupCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(GroupCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(GroupCreateView, self).post(request, *args, **kwargs)

    def get_form_class(self):
        return super(GroupCreateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(GroupCreateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(GroupCreateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(GroupCreateView, self).get_initial()

    def form_invalid(self, form):
        return super(GroupCreateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(GroupCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(GroupCreateView, self).get_context_data(**kwargs)
        return ret

    def render_to_response(self, context, **response_kwargs):
        return super(GroupCreateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(GroupCreateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:group_detail", args=(self.object.pk,))


class GroupUpdateView(UpdateView):
    model = Group
    form_class = GroupForm
    # fields = ['name', 'description', 'core_competency_1', 'core_competency_2', 'core_competency_3']
    template_name = "experiences/group_update.html"
    initial = {}
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "group"

    def __init__(self, **kwargs):
        return super(GroupUpdateView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        # Get the object
        self.object = self.get_object()
        
        # Check if user has permission to edit
        if not self.has_change_permission(request):
            raise PermissionDenied
            
        return super().dispatch(request, *args, **kwargs)

    def has_change_permission(self, request):
        # Superusers can edit anything
        if request.user.is_superuser:
            return True
        # Administrators can edit any group
        if request.user.groups.filter(name='Administrators').exists():
            return True
        # Check if the user is a facilitator and a member of this group
        try:
            person = request.user.person
            return person.role.title == 'Facilitator' and person in self.object.members.all()
        except:
            return False

    def get(self, request, *args, **kwargs):
        return super(GroupUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(GroupUpdateView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(GroupUpdateView, self).get_object(queryset)

    def get_queryset(self):
        return super(GroupUpdateView, self).get_queryset()

    def get_slug_field(self):
        return super(GroupUpdateView, self).get_slug_field()

    def get_form_class(self):
        return super(GroupUpdateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(GroupUpdateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(GroupUpdateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(GroupUpdateView, self).get_initial()

    def form_invalid(self, form):
        return super(GroupUpdateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(GroupUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(GroupUpdateView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(GroupUpdateView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(GroupUpdateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(GroupUpdateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:group_detail", args=(self.object.pk,))


class GroupDeleteView(DeleteView):
    model = Group
    template_name = "experiences/group_delete.html"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "group"

    def __init__(self, **kwargs):
        return super(GroupDeleteView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        # Get the object
        self.object = self.get_object()
        
        # Only superusers and administrators can delete
        if not (request.user.is_superuser or request.user.groups.filter(name='Administrators').exists()):
            raise PermissionDenied
            
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        return super(GroupDeleteView, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(GroupDeleteView, self).delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(GroupDeleteView, self).get_object(queryset)

    def get_queryset(self):
        return super(GroupDeleteView, self).get_queryset()

    def get_slug_field(self):
        return super(GroupDeleteView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(GroupDeleteView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(GroupDeleteView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(GroupDeleteView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(GroupDeleteView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:group_list")
