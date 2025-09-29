from django.db import models
from django.core.validators import MinValueValidator
from project.models import Project
from decimal import Decimal

class Unit(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True, null=False, blank= False)
    abbreviation = models.CharField("Abreviatura", max_length=10, unique=True, null=False, blank= False, help_text="Usa una abreviatura corta, p. ej., kg, m, u.") 

    class Meta:
        verbose_name = "Unidad"
        verbose_name_plural = "Unidades"
        ordering = ["name"]

    def __str__(self):  
        return f"{self.name} ({self.abbreviation})"


class Material(models.Model):
    name = models.CharField("Nombre", max_length=100, null=False, blank= False)
    description = models.TextField("Descripción del material", null=True, blank= True)
    price = models.DecimalField(
        "Precio",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False, blank= False
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,   
        null=True,                   
        blank=True,                  
        related_name="materials"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="proyecto_materiales"
    )

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        u = self.unit.abbreviation if self.unit else "sin unidad"
        return f"{self.name} - {u} - ${self.price} ({self.project})"


class Labour(models.Model):
    name = models.CharField("Nombre", max_length=100, null=False, blank= False)
    description = models.TextField("Descripción de la mano de obra", null=True, blank= True)
    price = models.DecimalField(
        "Valor de la jornada",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="proyecto_mano_de_obra"
    )

    class Meta:
        verbose_name = "Mano de obra"
        verbose_name_plural = "Listado mano de obra"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - ${self.price} ({self.project})"
    
class Tool(models.Model):
    name = models.CharField("Nombre", max_length=100, null=False, blank= False)
    dayCost = models.DecimalField(
        "Valor por día",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="proyecto_herramienta"
    )
    
    def __str__(self):
        return f"{self.name} - ${self.dayCost}"
    
    class Meta:
        verbose_name = "Herramienta o equipo"
        verbose_name_plural = "Herramientas y equipos"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]


