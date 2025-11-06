from django.db import models
from activity.models import Activity
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
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
        help_text="Estado del cronograma: Planeado, Ejecutando o Finalizado.",
        db_index=True,
    )


    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="schedule_activity",
        verbose_name="Actividad",
        help_text="Referencia a la actividad que pertenecen"
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = "Cronograma"
        verbose_name_plural = "Cronogramas"
        ordering = ["-start_date", "-created_at"]
        constraints = [
            # Garantiza end_date >= start_date a nivel de base de datos
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

     # Validaciones de negocio
    def clean(self):
        super().clean()

        if self.start_date is None or self.end_date is None:
            return  # El Required lo controlan los formularios/serializer

        # 1) end_date no puede ser anterior a start_date
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "La fecha de fin no puede ser anterior a la fecha de inicio."})

        # 2) Al CREAR: no se permiten fechas menores a hoy
        #    (Si también quieres bloquear en edición, quita la condición `if self.pk is None`)
        hoy = timezone.localdate()
        if self.pk is None:
            errors = {}
            if self.start_date < hoy:
                errors["start_date"] = "La fecha de inicio no puede ser menor a la fecha actual."
            if self.end_date < hoy:
                errors["end_date"] = "La fecha de fin no puede ser menor a la fecha actual."
            if errors:
                raise ValidationError(errors)

        # 3) (Opcional) Si el estado es FINALIZADO, exige que end_date sea hoy o anterior
        if self.status == self.Status.FINALIZADO and self.end_date > timezone.localdate():
            raise ValidationError({"status": "No puede marcarse como Finalizado si la fecha de fin es posterior a hoy."})
        
        # 4️) Validar que una actividad no tenga más de un cronograma
        existe_otro = (
            Schedule.objects
            .filter(activity=self.activity)
            .exclude(pk=self.pk)  # excluye el actual en caso de edición
            .exists()
        )
        if existe_otro:
            raise ValidationError({
                "activity": "Esta actividad ya tiene un cronograma asignado. No puede registrarse nuevamente."
            })

    # Asegura que se validen reglas antes de guardar
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
