from django.db import models
from django.contrib.auth.models import Group
# Create your models here.
def create_default_groups():
    # Create default user groups
    Group.objects.get_or_create(name='Ingeniero')
    Group.objects.get_or_create(name='Supervisor')
    Group.objects.get_or_create(name='Arquitecto')