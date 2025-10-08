from django.contrib import admin
from .models import memoryHeavyMachine, Activity
# Register your models here.

admin.site.register(Activity)
admin.site.register(memoryHeavyMachine)