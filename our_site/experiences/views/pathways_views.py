from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from ..models import Pathways
from ..forms import PathwaysForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import Http404


class PathwaysListView(ListView):
    model = Pathways
    template_name = "experiences/pathways_list.html"
    paginate_by = 20
    context_object_name = "pathways_list"
    allow_empty = True
    page_kwarg = 'page'
    paginate_orphans = 0

    def __init__(self, **kwargs):
        return super(PathwaysListView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(PathwaysListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(PathwaysListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return super(PathwaysListView, self).get_queryset()

    def get_allow_empty(self):
        return super(PathwaysListView, self).get_allow_empty()

    def get_context_data(self, *args, **kwargs):
        ret = super(PathwaysListView, self).get_context_data(*args, **kwargs)
        return ret

    def get_paginate_by(self, queryset):
        return super(PathwaysListView, self).get_paginate_by(queryset)

    def get_context_object_name(self, object_list):
        return super(PathwaysListView, self).get_context_object_name(object_list)

    def paginate_queryset(self, queryset, page_size):
        return super(PathwaysListView, self).paginate_queryset(queryset, page_size)

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return super(PathwaysListView, self).get_paginator(queryset, per_page, orphans=0, allow_empty_first_page=True)

    def render_to_response(self, context, **response_kwargs):
        return super(PathwaysListView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PathwaysListView, self).get_template_names()


class PathwaysDetailView(DetailView):
    model = Pathways
    template_name = "experiences/pathways_detail.html"
    context_object_name = "pathways"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def __init__(self, **kwargs):
        return super(PathwaysDetailView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(PathwaysDetailView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(PathwaysDetailView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(PathwaysDetailView, self).get_object(queryset)

    def get_queryset(self):
        return super(PathwaysDetailView, self).get_queryset()

    def get_slug_field(self):
        return super(PathwaysDetailView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(PathwaysDetailView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(PathwaysDetailView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(PathwaysDetailView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PathwaysDetailView, self).get_template_names()


class PathwaysCreateView(CreateView):
    model = Pathways
    form_class = PathwaysForm
    # fields = ['title', 'description', 'is_active']
    template_name = "experiences/pathways_create.html"
    success_url = reverse_lazy("pathways_list")

    def __init__(self, **kwargs):
        return super(PathwaysCreateView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super(PathwaysCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(PathwaysCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(PathwaysCreateView, self).post(request, *args, **kwargs)

    def get_form_class(self):
        return super(PathwaysCreateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(PathwaysCreateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(PathwaysCreateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(PathwaysCreateView, self).get_initial()

    def form_invalid(self, form):
        return super(PathwaysCreateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(PathwaysCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PathwaysCreateView, self).get_context_data(**kwargs)
        return ret

    def render_to_response(self, context, **response_kwargs):
        return super(PathwaysCreateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PathwaysCreateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:pathways_detail", args=(self.object.pk,))


class PathwaysUpdateView(UpdateView):
    model = Pathways
    form_class = PathwaysForm
    # fields = ['title', 'description', 'is_active']
    template_name = "experiences/pathways_update.html"
    initial = {}
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "pathways"

    def __init__(self, **kwargs):
        return super(PathwaysUpdateView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(PathwaysUpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(PathwaysUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(PathwaysUpdateView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(PathwaysUpdateView, self).get_object(queryset)

    def get_queryset(self):
        return super(PathwaysUpdateView, self).get_queryset()

    def get_slug_field(self):
        return super(PathwaysUpdateView, self).get_slug_field()

    def get_form_class(self):
        return super(PathwaysUpdateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(PathwaysUpdateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(PathwaysUpdateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(PathwaysUpdateView, self).get_initial()

    def form_invalid(self, form):
        return super(PathwaysUpdateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(PathwaysUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PathwaysUpdateView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(PathwaysUpdateView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(PathwaysUpdateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PathwaysUpdateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:pathways_detail", args=(self.object.pk,))


class PathwaysDeleteView(DeleteView):
    model = Pathways
    template_name = "experiences/pathways_delete.html"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "pathways"

    def __init__(self, **kwargs):
        return super(PathwaysDeleteView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(PathwaysDeleteView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        return super(PathwaysDeleteView, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(PathwaysDeleteView, self).delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(PathwaysDeleteView, self).get_object(queryset)

    def get_queryset(self):
        return super(PathwaysDeleteView, self).get_queryset()

    def get_slug_field(self):
        return super(PathwaysDeleteView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(PathwaysDeleteView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(PathwaysDeleteView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(PathwaysDeleteView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(PathwaysDeleteView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:pathways_list")
