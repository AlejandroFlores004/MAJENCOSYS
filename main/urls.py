from django.contrib import admin
from django.urls import path,include
from .views import startpage

urlpatterns = [
    path('', startpage, name='startpage'),
]