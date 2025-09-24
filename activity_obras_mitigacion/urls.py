from django.urls import path
from .views import mainActivityObrasMitigacion

urlpatterns = [
    path('', mainActivityObrasMitigacion, name='activity_obras_mitigacion'),
]