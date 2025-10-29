from django.urls import path
from .views import mainSchedule, schedule_start_page

urlpatterns = [
    path('', mainSchedule, name='schedule_home'),
        path(
        "comenzar_actividad/<int:activity_id>/",
        schedule_start_page,
        name="schedule_start_page",
    ),
]