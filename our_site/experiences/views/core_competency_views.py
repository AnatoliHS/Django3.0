from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from ..models import CoreCompetency
from ..forms import CoreCompetencyForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import Http404


class CoreCompetencyListView(ListView):
    model = CoreCompetency
    template_name = "experiences/core_competency_list.html"
    paginate_by = 20
    context_object_name = "core_competency_list"
    allow_empty = True
    page_kwarg = 'page'
    paginate_orphans = 0

    def __init__(self, **kwargs):
        return super(CoreCompetencyListView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(CoreCompetencyListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(CoreCompetencyListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return super(CoreCompetencyListView, self).get_queryset()

    def get_allow_empty(self):
        return super(CoreCompetencyListView, self).get_allow_empty()

    def get_context_data(self, *args, **kwargs):
        ret = super(CoreCompetencyListView, self).get_context_data(*args, **kwargs)
        return ret

    def get_paginate_by(self, queryset):
        return super(CoreCompetencyListView, self).get_paginate_by(queryset)

    def get_context_object_name(self, object_list):
        return super(CoreCompetencyListView, self).get_context_object_name(object_list)

    def paginate_queryset(self, queryset, page_size):
        return super(CoreCompetencyListView, self).paginate_queryset(queryset, page_size)

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return super(CoreCompetencyListView, self).get_paginator(queryset, per_page, orphans=0, allow_empty_first_page=True)

    def render_to_response(self, context, **response_kwargs):
        return super(CoreCompetencyListView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(CoreCompetencyListView, self).get_template_names()


class CoreCompetencyDetailView(DetailView):
    model = CoreCompetency
    template_name = "experiences/core_competency_detail.html"
    context_object_name = "core_competency"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def __init__(self, **kwargs):
        return super(CoreCompetencyDetailView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(CoreCompetencyDetailView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(CoreCompetencyDetailView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(CoreCompetencyDetailView, self).get_object(queryset)

    def get_queryset(self):
        return super(CoreCompetencyDetailView, self).get_queryset()

    def get_slug_field(self):
        return super(CoreCompetencyDetailView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(CoreCompetencyDetailView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(CoreCompetencyDetailView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(CoreCompetencyDetailView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(CoreCompetencyDetailView, self).get_template_names()


class CoreCompetencyCreateView(CreateView):
    model = CoreCompetency
    form_class = CoreCompetencyForm
    # fields = ['title', 'description', 'is_active']
    template_name = "experiences/core_competency_create.html"
    success_url = reverse_lazy("core_competency_list")

    def __init__(self, **kwargs):
        return super(CoreCompetencyCreateView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super(CoreCompetencyCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(CoreCompetencyCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(CoreCompetencyCreateView, self).post(request, *args, **kwargs)

    def get_form_class(self):
        return super(CoreCompetencyCreateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(CoreCompetencyCreateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(CoreCompetencyCreateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(CoreCompetencyCreateView, self).get_initial()

    def form_invalid(self, form):
        return super(CoreCompetencyCreateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(CoreCompetencyCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(CoreCompetencyCreateView, self).get_context_data(**kwargs)
        return ret

    def render_to_response(self, context, **response_kwargs):
        return super(CoreCompetencyCreateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(CoreCompetencyCreateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:core_competency_detail", args=(self.object.pk,))


class CoreCompetencyUpdateView(UpdateView):
    model = CoreCompetency
    form_class = CoreCompetencyForm
    # fields = ['title', 'description', 'is_active']
    template_name = "experiences/core_competency_update.html"
    initial = {}
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "core_competency"

    def __init__(self, **kwargs):
        return super(CoreCompetencyUpdateView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(CoreCompetencyUpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(CoreCompetencyUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(CoreCompetencyUpdateView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(CoreCompetencyUpdateView, self).get_object(queryset)

    def get_queryset(self):
        return super(CoreCompetencyUpdateView, self).get_queryset()

    def get_slug_field(self):
        return super(CoreCompetencyUpdateView, self).get_slug_field()

    def get_form_class(self):
        return super(CoreCompetencyUpdateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(CoreCompetencyUpdateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(CoreCompetencyUpdateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(CoreCompetencyUpdateView, self).get_initial()

    def form_invalid(self, form):
        return super(CoreCompetencyUpdateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(CoreCompetencyUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(CoreCompetencyUpdateView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(CoreCompetencyUpdateView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(CoreCompetencyUpdateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(CoreCompetencyUpdateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:core_competency_detail", args=(self.object.pk,))


class CoreCompetencyDeleteView(DeleteView):
    model = CoreCompetency
    template_name = "experiences/core_competency_delete.html"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "core_competency"

    def __init__(self, **kwargs):
        return super(CoreCompetencyDeleteView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(CoreCompetencyDeleteView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        return super(CoreCompetencyDeleteView, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(CoreCompetencyDeleteView, self).delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(CoreCompetencyDeleteView, self).get_object(queryset)

    def get_queryset(self):
        return super(CoreCompetencyDeleteView, self).get_queryset()

    def get_slug_field(self):
        return super(CoreCompetencyDeleteView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(CoreCompetencyDeleteView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(CoreCompetencyDeleteView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(CoreCompetencyDeleteView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(CoreCompetencyDeleteView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:core_competency_list")
