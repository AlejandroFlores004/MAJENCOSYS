from django.contrib import admin
from .models import Material,Unit,ManoObra,Herramienta,Equipo

# Register your models here.
admin.site.register(Equipo)
admin.site.register(Herramienta)
admin.site.register(ManoObra)
admin.site.register(Material)
admin.site.register(Unit)