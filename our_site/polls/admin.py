from django.contrib import admin

from .models import Question, Choice
from .models import Certificate

class ChoiceInline(admin.TabularInline):

    extra = 0
    model = Choice

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    pass

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'issued_at', 'image')
    search_fields = ('user__username',)
    list_filter = ('issued_at',)
    readonly_fields = ('issued_at',)

    def has_add_permission(self, request):
        return False




