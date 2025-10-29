from django.contrib import admin
from .models import ReportTemplate

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "owner", "updated_at")
    list_filter  = ("project", "owner")
    search_fields = ("name",)
