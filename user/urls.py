from django.contrib import admin
from django.urls import path,include
from .views import userMain

urlpatterns = [
    path('', userMain, name='usuariosMain'),
]