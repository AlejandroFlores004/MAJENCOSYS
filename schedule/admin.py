from django.contrib import admin
from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("activity", "start_date", "end_date", "status")
    list_filter = ("status",)
    search_fields = ("activity__name",)
