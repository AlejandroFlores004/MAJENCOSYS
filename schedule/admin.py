from django.contrib import admin
from .models import schedule  # <- tu modelo se llama 'schedule' (minúscula)

@admin.register(schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("activity", "start_date", "end_date", "status", "created_at")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("activity__name",)
