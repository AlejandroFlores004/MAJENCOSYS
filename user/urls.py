from django.contrib import admin
from django.urls import path,include
from .views import userMain,userFormView

urlpatterns = [
    path('', userMain, name='usuariosMain'),
    path('/formulario_usuario', userFormView, name='usuarioForm'),
]