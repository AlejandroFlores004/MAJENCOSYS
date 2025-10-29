from django.conf import settings
from django.db import models
from django.db.models import JSONField  # JSONField nativo de Django (no requiere Postgres)
from project.models import Project

class ReportTemplate(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='report_templates'
    )
    name = models.CharField(max_length=120)
    # Guardamos las opciones del constructor: columns, filters, order, group_by...
    payload = JSONField(default=dict, blank=True)

    # 👇 NUEVO: quién creó/posee la plantilla (opcional si no quieres obligar login)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='report_templates'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('project', 'name')  # mismo nombre no se repite dentro del proyecto

    def __str__(self):
        who = f' · {self.owner}' if self.owner else ''
        return f'{self.project_id} · {self.name}{who}'
