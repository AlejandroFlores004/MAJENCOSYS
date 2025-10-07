from django.contrib import admin
from .models import Unit, Material, Labour, Tool, HeavyMachinery, QualityControl

# Register your models here.
admin.site.register(Unit)
admin.site.register(Material)
admin.site.register(Labour)
admin.site.register(Tool)
admin.site.register(HeavyMachinery)
admin.site.register(QualityControl)