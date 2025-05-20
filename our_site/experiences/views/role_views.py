from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from ..models import Role
from ..forms import RoleForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import Http404


class RoleListView(ListView):
    model = Role
    template_name = "experiences/role_list.html"
    paginate_by = 20
    context_object_name = "role_list"
    allow_empty = True
    page_kwarg = 'page'
    paginate_orphans = 0

    def __init__(self, **kwargs):
        return super(RoleListView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(RoleListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(RoleListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return super(RoleListView, self).get_queryset()

    def get_allow_empty(self):
        return super(RoleListView, self).get_allow_empty()

    def get_context_data(self, *args, **kwargs):
        ret = super(RoleListView, self).get_context_data(*args, **kwargs)
        return ret

    def get_paginate_by(self, queryset):
        return super(RoleListView, self).get_paginate_by(queryset)

    def get_context_object_name(self, object_list):
        return super(RoleListView, self).get_context_object_name(object_list)

    def paginate_queryset(self, queryset, page_size):
        return super(RoleListView, self).paginate_queryset(queryset, page_size)

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return super(RoleListView, self).get_paginator(queryset, per_page, orphans=0, allow_empty_first_page=True)

    def render_to_response(self, context, **response_kwargs):
        return super(RoleListView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(RoleListView, self).get_template_names()


class RoleDetailView(DetailView):
    model = Role
    template_name = "experiences/role_detail.html"
    context_object_name = "role"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def __init__(self, **kwargs):
        return super(RoleDetailView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(RoleDetailView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(RoleDetailView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(RoleDetailView, self).get_object(queryset)

    def get_queryset(self):
        return super(RoleDetailView, self).get_queryset()

    def get_slug_field(self):
        return super(RoleDetailView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(RoleDetailView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(RoleDetailView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(RoleDetailView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(RoleDetailView, self).get_template_names()


class RoleCreateView(CreateView):
    model = Role
    form_class = RoleForm
    # fields = ['title', 'description', 'is_active']
    template_name = "experiences/role_create.html"
    success_url = reverse_lazy("role_list")

    def __init__(self, **kwargs):
        return super(RoleCreateView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super(RoleCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(RoleCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(RoleCreateView, self).post(request, *args, **kwargs)

    def get_form_class(self):
        return super(RoleCreateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(RoleCreateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(RoleCreateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(RoleCreateView, self).get_initial()

    def form_invalid(self, form):
        return super(RoleCreateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(RoleCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(RoleCreateView, self).get_context_data(**kwargs)
        return ret

    def render_to_response(self, context, **response_kwargs):
        return super(RoleCreateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(RoleCreateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:role_detail", args=(self.object.pk,))


class RoleUpdateView(UpdateView):
    model = Role
    form_class = RoleForm
    # fields = ['title', 'description', 'is_active']
    template_name = "experiences/role_update.html"
    initial = {}
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "role"

    def __init__(self, **kwargs):
        return super(RoleUpdateView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(RoleUpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(RoleUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(RoleUpdateView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(RoleUpdateView, self).get_object(queryset)

    def get_queryset(self):
        return super(RoleUpdateView, self).get_queryset()

    def get_slug_field(self):
        return super(RoleUpdateView, self).get_slug_field()

    def get_form_class(self):
        return super(RoleUpdateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(RoleUpdateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(RoleUpdateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(RoleUpdateView, self).get_initial()

    def form_invalid(self, form):
        return super(RoleUpdateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(RoleUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(RoleUpdateView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(RoleUpdateView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(RoleUpdateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(RoleUpdateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:role_detail", args=(self.object.pk,))


class RoleDeleteView(DeleteView):
    model = Role
    template_name = "experiences/role_delete.html"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "role"

    def __init__(self, **kwargs):
        return super(RoleDeleteView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(RoleDeleteView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        return super(RoleDeleteView, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(RoleDeleteView, self).delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(RoleDeleteView, self).get_object(queryset)

    def get_queryset(self):
        return super(RoleDeleteView, self).get_queryset()

    def get_slug_field(self):
        return super(RoleDeleteView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(RoleDeleteView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(RoleDeleteView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(RoleDeleteView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(RoleDeleteView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:role_list")
