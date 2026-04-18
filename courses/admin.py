from django.contrib import admin
from django.contrib.auth.models import User
from .models import Lesson, Question, Choice, Submission


class QuestionInline(admin.TabularInline):
    """Inline admin for Question model."""
    model = Question
    extra = 1
    fields = ['question_text', 'question_type', 'order']


class ChoiceInline(admin.TabularInline):
    """Inline admin for Choice model."""
    model = Choice
    extra = 1
    fields = ['choice_text', 'is_correct', 'order']


class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for Question model."""
    list_display = ['question_text', 'lesson', 'question_type', 'order']
    list_filter = ['lesson', 'question_type']
    search_fields = ['question_text']
    inlines = [ChoiceInline]
    fieldsets = (
        ('Question Information', {
            'fields': ('lesson', 'question_text', 'question_type')
        }),
        ('Ordering', {
            'fields': ('order',)
        }),
    )


class LessonAdmin(admin.ModelAdmin):
    """Admin configuration for Lesson model."""
    list_display = ['title', 'description', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuestionInline]
    fieldsets = (
        ('Lesson Information', {
            'fields': ('title', 'description', 'content')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class SubmissionAdmin(admin.ModelAdmin):
    """Admin configuration for Submission model."""
    list_display = ['user', 'lesson', 'score', 'total_questions', 'submitted_at']
    list_filter = ['lesson', 'submitted_at']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['submitted_at', 'score', 'total_questions']
    fieldsets = (
        ('Submission Information', {
            'fields': ('user', 'lesson')
        }),
        ('Results', {
            'fields': ('score', 'total_questions')
        }),
        ('Metadata', {
            'fields': ('submitted_at',)
        }),
    )


# Register models
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission, SubmissionAdmin)
