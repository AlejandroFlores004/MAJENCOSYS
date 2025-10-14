from django.contrib import admin
from .models import Activity, MemoryMaterial, MemoryManoObra, MemoryHerramienta, MemoryEquipo, Header
# Register your models here.
admin.site.register(Activity)
admin.site.register(MemoryMaterial)
admin.site.register(MemoryManoObra)
admin.site.register(MemoryHerramienta)
admin.site.register(MemoryEquipo)
admin.site.register(Header)
