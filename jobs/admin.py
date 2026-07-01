"""Admin configuration for jobs app."""

from django.contrib import admin
from .models import Job, JobCategory, JobSavedByUser


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    """Admin for JobCategory."""

    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin for Job."""

    list_display = (
        'title',
        'employer',
        'job_type',
        'location',
        'is_active',
        'created_at')
    list_filter = (
        'job_type',
        'is_active',
        'is_featured',
        'is_remote',
        'created_at',
        'category')
    search_fields = ('title', 'description', 'employer__email', 'location')
    readonly_fields = ('views_count', 'applications_count', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'slug', 'description', 'job_type', 'category')
        }),
        ('Location & Remote', {
            'fields': ('location', 'is_remote')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'currency')
        }),
        ('Requirements', {
            'fields': ('experience_level', 'required_skills')
        }),
        ('Employer', {
            'fields': ('employer',)
        }),
        ('Status & Visibility', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('views_count', 'applications_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-created_at',)


@admin.register(JobSavedByUser)
class JobSavedByUserAdmin(admin.ModelAdmin):
    """Admin for saved jobs."""

    list_display = ('candidate', 'job', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('candidate__email', 'job__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
