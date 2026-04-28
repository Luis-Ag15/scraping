from django.contrib import admin
from .models import SearchConfig, JobResult


class JobResultInline(admin.TabularInline):
    model = JobResult
    extra = 0
    readonly_fields = ('job_id', 'site', 'title', 'company', 'location', 'job_url')
    fields = ('site', 'title', 'company', 'location', 'job_url')


@admin.register(SearchConfig)
class SearchConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'search_terms', 'status', 'total_jobs_found', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [JobResultInline]


@admin.register(JobResult)
class JobResultAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'site', 'search')
    list_filter = ('site', 'search')
    search_fields = ('title', 'company', 'location')
