from django.db import models
from project.models import Project
from activity_catalogs.models import Material, Tool, Labour, HeavyMachinery, QualityControl
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
# Create your models here.

class Activity(models.Model):
    number = models.IntegerField("Número de la actividad", null=True, blank=True    )
    name = models.CharField("Nombre de la actividad",max_length=255, null=False, blank=False)
    description = models.TextField("Descripción de la actividad", null=False, blank=False)
    unit = models.CharField("Unidad", max_length=100, null=False, blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities_cmrv')
    tramo = models.CharField("Tramo",max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ['number']

    def __str__(self):
        return f"{self.number} - {self.name} ({self.project})"
    
    def save(self, *args, **kwargs):
        if self.number is None or self.number == 0:
            last_number = Activity.objects.filter(project=self.project).aggregate(models.Max('number'))['number__max']
            
            self.number = 1 if last_number is None else last_number + 1

        super().save(*args, **kwargs)
    
class memoryMaterial(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='memory_materials_cmrv')
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, related_name='memory_catalogue_materials_cmrv', null=True)
    quantity = models.DecimalField("Cantidad", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], null=False, blank=False)

    class Meta:
        verbose_name = "Memoria de Cálculo de Material"
        verbose_name_plural = "Memorias de Cálculo de Materiales"

    def __str__(self):
        total = round(self.quantity * self.material.price, 2)  # Redondea a 2 decimales
        return f"{self.material.name} - {self.material.unit.name}  - {self.quantity} - {self.material.price} - {total} ({self.activity})"


class memoryLabour(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='memory_labours_cmrv')
    labour = models.ForeignKey(Labour, on_delete=models.SET_NULL, related_name='memory_catalogue_labours_cmrv', null=True)
    prestation = models.DecimalField("Prestación", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01")), MaxValueValidator(Decimal("1"))], null=False, blank=False)
    performance = models.DecimalField("Total Jornadas de Trabajo", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], null=False, blank=False)
    class Meta:
        verbose_name = "Memoria de Cálculo de Mano de Obra"
        verbose_name_plural = "Memorias de Cálculo de Manos de Obra"

    def __str__(self):
        totalWorking = round(self.labour.price / (1-self.prestation), 2)
        total = round(totalWorking / self.performance, 2)
        return f"{self.labour.name} - {self.labour.price} - {self.prestation} - {totalWorking} - {self.performance} - {total} ({self.activity})"

class memoryTool(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='memory_tools_cmrv')
    tool = models.ForeignKey(Tool, on_delete=models.SET_NULL, related_name='memory_catalogue_tools_cmrv', null=True)
    performance = models.DecimalField("Rendimiento", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], null=False, blank=False)
    class Meta:
        verbose_name = "Memoria de Cálculo de Herramienta"
        verbose_name_plural = "Memorias de Cálculo de Herramientas"

    def __str__(self):
        total = round(self.tool.dayCost * self.performance, 2)
        return f"{self.tool.name} - {self.tool.dayCost} - {self.performance} - {total} ({self.activity})"
    
class memoryHeavyMachine(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='memory_heavy_cmrv')
    heavyMachinery = models.ForeignKey(HeavyMachinery, on_delete=models.SET_NULL, related_name='memory_catalogue_heavy_machine_cmrv', null=True)
    performance = models.DecimalField("Rendimiento", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], null=False, blank=False)

    class Meta:
        verbose_name = "Memoria de Cálculo de Maquinaria Pesada"
        verbose_name_plural = "Memorias de Cálculo Maquinarias Pesadas"

    def __str__(self):
        total = round(self.heavyMachinery.price * self.performance, 2)
        return f"{self.heavyMachinery.name} - {self.heavyMachinery.price} - {self.performance} - {total} ({self.activity})"
