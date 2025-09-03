from django.contrib import admin
from django.urls import path,include
from .views import startpage,dashboard,loginPage

urlpatterns = [
    path('', startpage, name='startpage'),
    path('dashboard', dashboard, name='dash'),
    path('login/',loginPage, name='log'),
    path('admon_usuarios/',include('user.urls'),name='user')
]