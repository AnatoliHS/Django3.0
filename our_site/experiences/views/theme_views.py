from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from ..models import Theme
from ..forms import ThemeForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import Http404


class ThemeListView(ListView):
    model = Theme
    template_name = "experiences/theme_list.html"
    paginate_by = 20
    context_object_name = "theme_list"
    allow_empty = True
    page_kwarg = 'page'
    paginate_orphans = 0

    def __init__(self, **kwargs):
        return super(ThemeListView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(ThemeListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(ThemeListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return super(ThemeListView, self).get_queryset()

    def get_allow_empty(self):
        return super(ThemeListView, self).get_allow_empty()

    def get_context_data(self, *args, **kwargs):
        ret = super(ThemeListView, self).get_context_data(*args, **kwargs)
        return ret

    def get_paginate_by(self, queryset):
        return super(ThemeListView, self).get_paginate_by(queryset)

    def get_context_object_name(self, object_list):
        return super(ThemeListView, self).get_context_object_name(object_list)

    def paginate_queryset(self, queryset, page_size):
        return super(ThemeListView, self).paginate_queryset(queryset, page_size)

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return super(ThemeListView, self).get_paginator(queryset, per_page, orphans=0, allow_empty_first_page=True)

    def render_to_response(self, context, **response_kwargs):
        return super(ThemeListView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(ThemeListView, self).get_template_names()


class ThemeDetailView(DetailView):
    model = Theme
    template_name = "experiences/theme_detail.html"
    context_object_name = "theme"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def __init__(self, **kwargs):
        return super(ThemeDetailView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(ThemeDetailView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(ThemeDetailView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(ThemeDetailView, self).get_object(queryset)

    def get_queryset(self):
        return super(ThemeDetailView, self).get_queryset()

    def get_slug_field(self):
        return super(ThemeDetailView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(ThemeDetailView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(ThemeDetailView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(ThemeDetailView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(ThemeDetailView, self).get_template_names()


class ThemeCreateView(CreateView):
    model = Theme
    form_class = ThemeForm
    # fields = ['group', 'color_palette', 'font_choices', 'logo', 'background_image']
    template_name = "experiences/theme_create.html"
    success_url = reverse_lazy("theme_list")

    def __init__(self, **kwargs):
        return super(ThemeCreateView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super(ThemeCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(ThemeCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(ThemeCreateView, self).post(request, *args, **kwargs)

    def get_form_class(self):
        return super(ThemeCreateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(ThemeCreateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(ThemeCreateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(ThemeCreateView, self).get_initial()

    def form_invalid(self, form):
        return super(ThemeCreateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(ThemeCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(ThemeCreateView, self).get_context_data(**kwargs)
        return ret

    def render_to_response(self, context, **response_kwargs):
        return super(ThemeCreateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(ThemeCreateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:theme_detail", args=(self.object.pk,))


class ThemeUpdateView(UpdateView):
    model = Theme
    form_class = ThemeForm
    # fields = ['group', 'color_palette', 'font_choices', 'logo', 'background_image']
    template_name = "experiences/theme_update.html"
    initial = {}
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "theme"

    def __init__(self, **kwargs):
        return super(ThemeUpdateView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(ThemeUpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(ThemeUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(ThemeUpdateView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(ThemeUpdateView, self).get_object(queryset)

    def get_queryset(self):
        return super(ThemeUpdateView, self).get_queryset()

    def get_slug_field(self):
        return super(ThemeUpdateView, self).get_slug_field()

    def get_form_class(self):
        return super(ThemeUpdateView, self).get_form_class()

    def get_form(self, form_class=None):
        return super(ThemeUpdateView, self).get_form(form_class)

    def get_form_kwargs(self, **kwargs):
        return super(ThemeUpdateView, self).get_form_kwargs(**kwargs)

    def get_initial(self):
        return super(ThemeUpdateView, self).get_initial()

    def form_invalid(self, form):
        return super(ThemeUpdateView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return super(ThemeUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(ThemeUpdateView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(ThemeUpdateView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(ThemeUpdateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(ThemeUpdateView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:theme_detail", args=(self.object.pk,))


class ThemeDeleteView(DeleteView):
    model = Theme
    template_name = "experiences/theme_delete.html"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = "theme"

    def __init__(self, **kwargs):
        return super(ThemeDeleteView, self).__init__(**kwargs)

    def dispatch(self, *args, **kwargs):
        return super(ThemeDeleteView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        return super(ThemeDeleteView, self).post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(ThemeDeleteView, self).delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super(ThemeDeleteView, self).get_object(queryset)

    def get_queryset(self):
        return super(ThemeDeleteView, self).get_queryset()

    def get_slug_field(self):
        return super(ThemeDeleteView, self).get_slug_field()

    def get_context_data(self, **kwargs):
        ret = super(ThemeDeleteView, self).get_context_data(**kwargs)
        return ret

    def get_context_object_name(self, obj):
        return super(ThemeDeleteView, self).get_context_object_name(obj)

    def render_to_response(self, context, **response_kwargs):
        return super(ThemeDeleteView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        return super(ThemeDeleteView, self).get_template_names()

    def get_success_url(self):
        return reverse("experiences:theme_list")
