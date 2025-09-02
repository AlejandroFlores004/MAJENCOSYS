from django.contrib import admin
from django.urls import path,include
from .views import userMain,userFormView,userDetails,userEdit,userEditPassword

urlpatterns = [
    path('', userMain, name='usuariosMain'),
    path('formulario_usuario/', userFormView, name='usuarioForm'),
    path('detalles_usuarios/', userDetails, name='usuarioDetails'),
    path('usuario/<int:pk>/editar/', userEdit, name='usuarioEdit'),
    path('usuario/<int:pk>/editarPassword/', userEditPassword, name='usuarioEditPass'),
]