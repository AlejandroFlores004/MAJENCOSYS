from django.urls import path
from .views import mainActivityCrmv

urlpatterns = [
    path('', mainActivityCrmv, name='activity_cmrv'),
]