from django.contrib import admin

from .models import Question, Choice

class ChoiceInline(admin.TabularInline):
    extra = 0
    model = Choice

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    pass




