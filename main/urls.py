from django.contrib import admin
from django.urls import path,include
from .views import startpage

urlpatterns = [
    path('', startpage, name='startpage'),
    path('admon_usuarios',include('user.urls'),name='user')
]