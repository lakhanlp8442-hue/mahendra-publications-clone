from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, JournalIssue, Article, ReviewAssignment

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Academic Profile', {'fields': ('role', 'affiliation', 'orcid_id')}),
    )
    list_display = ('username', 'email', 'role', 'affiliation')

@admin.register(JournalIssue)
class JournalIssueAdmin(admin.ModelAdmin):
    list_display = ('volume', 'issue', 'month_year', 'is_current')
    list_editable = ('is_current',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'title', 'status', 'issue', 'doi', 'submitted_at')
    list_filter = ('status', 'issue')
    search_fields = ('tracking_id', 'title', 'authors_list', 'keywords')
    list_editable = ('status', 'issue')

@admin.register(ReviewAssignment)
class ReviewAssignmentAdmin(admin.ModelAdmin):
    list_display = ('article', 'reviewer', 'recommendation', 'assigned_at')
    list_filter = ('recommendation',)