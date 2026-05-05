"""Admin configuration for applications app."""

from django.contrib import admin
from .models import Application, ApplicationNote, ApplicationStatusHistory


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin for Application."""
    
    list_display = ('candidate', 'job', 'status', 'rating', 'created_at')
    list_filter = ('status', 'rating', 'created_at', 'updated_at')
    search_fields = ('candidate__email', 'job__title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Application Info', {
            'fields': ('candidate', 'job', 'resume', 'cover_letter')
        }),
        ('Status & Rating', {
            'fields': ('status', 'rating', 'notes', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(ApplicationNote)
class ApplicationNoteAdmin(admin.ModelAdmin):
    """Admin for ApplicationNote."""
    
    list_display = ('application', 'employer', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('application__candidate__email', 'employer__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    """Admin for ApplicationStatusHistory."""
    
    list_display = ('application', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = ('application__candidate__email', 'changed_by__email')
    readonly_fields = ('changed_at',)
    ordering = ('-changed_at',)
