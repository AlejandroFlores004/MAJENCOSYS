from django.contrib import admin
from .models import Activity, memoryMaterial, memoryLabour, memoryTool

# Register your models here.
admin.site.register(Activity)
admin.site.register(memoryMaterial)
admin.site.register(memoryLabour)
admin.site.register(memoryTool)