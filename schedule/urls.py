from django.urls import path
from .views import mainSchedule

urlpatterns = [
    path('', mainSchedule, name='schedule_home'),
]