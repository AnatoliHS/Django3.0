from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from ..models import Badges
from ..forms import BadgesForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import Http404


class BadgesListView(ListView):
    model = Badges
    template_name = "experiences/badges_list.html"
    paginate_by = 20
    context_object_name = "badges_list"
    allow_empty = True
    page_kwarg = 'page'
    paginate_orphans = 0

    def __init__(self, **kwargs):
        return super(BadgesListView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(BadgesListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(BadgesListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return super(BadgesListView, self).get_queryset()

    def get_allow_empty(self):
        return super(BadgesListView, self).get_allow_empty()

    def get_context_data(self, *args, **kwargs):
        ret = super(BadgesListView, self).get_context_data(*args, **kwargs)
        return ret

    def get_paginate_by(self, queryset):
        return super(BadgesListView, self).get_paginate_by(queryset)

    def get_context_object_name(self, object_list):
        return super(BadgesListView, self).get_context_object_name(object_list)

    def paginate_queryset(self, queryset, page_size):
        return super(BadgesListView, self).paginate_queryset(queryset, page_size)

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return super(BadgesListView, self).get_paginator(queryset, per_page, orphans=0, allow_empty_first_page=True)

    def render_to_response(self, context, **response_kwargs):
        return super(BadgesListView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(BadgesListView, self).get_template_names()


class BadgesDetailView(DetailView):
    model = Badges
    template_name = "experiences/badges_detail.html"
    context_object_name = "badges"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def __init__(self, **kwargs):
        return super(BadgesDetailView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(BadgesDetailView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(BadgesDetailView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(BadgesDetailView, self).get_object(queryset)

    def get_queryset(self):
        return super(BadgesDetailView, self).get_queryset()

    def get_slug_field(self):
        return super(BadgesDetailView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(BadgesDetailView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(BadgesDetailView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(BadgesDetailView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(BadgesDetailView, self).get_template_names()


class BadgesCreateView(CreateView):
    model = Badges
    form_class = BadgesForm
    # fields = ['title', 'description', 'image', 'is_active']
    template_name = "experiences/badges_create.html"
    success_url = reverse_lazy("badges_list")

    def __init__(self, **kwargs):
        return super(BadgesCreateView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super(BadgesCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(BadgesCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BadgesCreateView, self).post(request, *args, **kwargs)

    def get_form_class(self):
        return super(BadgesCreateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(BadgesCreateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(BadgesCreateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(BadgesCreateView, self).get_initial()

    def form_invalid(self, form):
        return super(BadgesCreateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(BadgesCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(BadgesCreateView, self).get_context_data(**kwargs)
        return ret

    def render_to_response(self, context, **response_kwargs):
        return super(BadgesCreateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(BadgesCreateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:badges_detail", args=(self.object.pk,))


class BadgesUpdateView(UpdateView):
    model = Badges
    form_class = BadgesForm
    # fields = ['title', 'description', 'image', 'is_active']
    template_name = "experiences/badges_update.html"
    initial = {}
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "badges"

    def __init__(self, **kwargs):
        return super(BadgesUpdateView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(BadgesUpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(BadgesUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BadgesUpdateView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(BadgesUpdateView, self).get_object(queryset)

    def get_queryset(self):
        return super(BadgesUpdateView, self).get_queryset()

    def get_slug_field(self):
        return super(BadgesUpdateView, self).get_slug_field()

    def get_form_class(self):
        return super(BadgesUpdateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(BadgesUpdateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(BadgesUpdateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(BadgesUpdateView, self).get_initial()

    def form_invalid(self, form):
        return super(BadgesUpdateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(BadgesUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(BadgesUpdateView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(BadgesUpdateView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(BadgesUpdateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(BadgesUpdateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:badges_detail", args=(self.object.pk,))


class BadgesDeleteView(DeleteView):
    model = Badges
    template_name = "experiences/badges_delete.html"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "badges"

    def __init__(self, **kwargs):
        return super(BadgesDeleteView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(BadgesDeleteView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        return super(BadgesDeleteView, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(BadgesDeleteView, self).delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(BadgesDeleteView, self).get_object(queryset)

    def get_queryset(self):
        return super(BadgesDeleteView, self).get_queryset()

    def get_slug_field(self):
        return super(BadgesDeleteView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(BadgesDeleteView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(BadgesDeleteView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(BadgesDeleteView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(BadgesDeleteView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:badges_list")
