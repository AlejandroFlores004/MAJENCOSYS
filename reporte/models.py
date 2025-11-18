from django.db import models
from project.models import Project


class ReportTemplate(models.Model):
    """
    Plantilla/report personalizado guardado por proyecto.
    Aquí se guarda el JSON que arma el reporte (columns, filters, order, group_by, name, etc.)
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="report_templates",
    )
    name = models.CharField(max_length=120)

    # Aquí vive TODO el constructor del reporte (columns, filters, order, group_by, etc.)
    payload = models.JSONField(default=dict, blank=True)

    # --- NUEVO: snapshot opcional de los datos generados por este reporte ---
    snapshot_data = models.JSONField(null=True, blank=True)
    snapshot_created_at = models.DateTimeField(null=True, blank=True)
    # -----------------------------------------------------------------------

    # Quién lo creó (opcional)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_templates",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        # evita que en el mismo proyecto haya dos reportes con el mismo nombre
        unique_together = ("project", "name")

    def __str__(self):
        who = f" · {self.owner}" if self.owner else ""
        return f"{self.project_id} · {self.name}{who}"

    # --- NUEVO: para saber si ya tiene datos guardados ---
    def has_snapshot(self):
        return bool(self.snapshot_data)
