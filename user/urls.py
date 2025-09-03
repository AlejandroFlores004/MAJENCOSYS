from django.contrib import admin
from django.urls import path,include
from .views import userMain,userFormView,userDetails,userEdit,userEditPassword,userEditStatus,userDelete

urlpatterns = [
    path('', userMain, name='usuariosMain'),
    path('formulario_usuario/', userFormView, name='usuarioForm'),
    path('detalles_usuarios/', userDetails, name='usuarioDetails'),
    path('usuario/<int:pk>/editar/', userEdit, name='usuarioEdit'),
    path('usuario/<int:pk>/editarPassword/', userEditPassword, name='usuarioEditPass'),
    path('usuario/<int:pk>/cambiarEstado/', userEditStatus, name='usuarioEditStatus'),
    path('usuario/<int:pk>/eliminar/', userDelete, name='usuarioDelete'),
]