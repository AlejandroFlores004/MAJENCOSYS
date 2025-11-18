# schedule/models.py
from django.db import models
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.utils import timezone

from activity.models import Activity


class Schedule(models.Model):
    class Status(models.TextChoices):
        PLANEADO = "P", "Planeado"
        EJECUTANDO = "E", "Ejecutando"
        FINALIZADO = "F", "Finalizado"

    start_date = models.DateField(
        verbose_name="Fecha de inicio",
        help_text="Fecha en la que inicia la actividad.",
        db_index=True,
    )
    end_date = models.DateField(
        verbose_name="Fecha de fin",
        help_text="Fecha en la que finaliza la actividad.",
        db_index=True,
    )
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.PLANEADO,
        verbose_name="Estado",
        help_text="Estado del cronograma",
        db_index=True,
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name="Actividad",
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = "Cronograma"
        verbose_name_plural = "Cronogramas"
        ordering = ["-start_date", "-created_at"]
        constraints = [
            models.CheckConstraint(
                check=Q(end_date__gte=F("start_date")),
                name="schedule_end_gte_start",
            ),
            models.UniqueConstraint(
                fields=["activity"],
                name="unique_schedule_per_activity",
            ),
        ]

    def __str__(self):
        return f"{self.activity} · {self.start_date} → {self.end_date} ({self.get_status_display()})"

    def clean(self):
        super().clean()

        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "La fecha de fin no puede ser menor que la de inicio."})

        today = timezone.localdate()

        # al crear
        if self.pk is None:
            errors = {}
            if self.start_date and self.start_date < today:
                errors["start_date"] = "La fecha de inicio no puede ser menor a hoy."
            if self.end_date and self.end_date < today:
                errors["end_date"] = "La fecha de fin no puede ser menor a hoy."
            if errors:
                raise ValidationError(errors)

        # solo 1 cronograma por actividad
        exists_other = (
            Schedule.objects.filter(activity=self.activity)
            .exclude(pk=self.pk)
            .exists()
        )
        if exists_other:
            raise ValidationError({"activity": "Esta actividad ya tiene cronograma."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
