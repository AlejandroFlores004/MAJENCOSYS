from django.contrib import admin
from django.urls import path,include
from .views import startpage,dashboard

urlpatterns = [
    path('', startpage, name='startpage'),
    path('dashboard',dashboard,name='dashboard'),
    path('admon_usuarios',include('user.urls'),name='user'),
    path('admon_project',include('project.urls'),name='project')
]
