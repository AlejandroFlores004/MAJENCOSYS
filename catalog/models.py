from django.db import models
from project.models import Project
from django.core.validators import MinLengthValidator, MinValueValidator
from decimal import Decimal

# Create your models here.

class Unit(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank= False,
        verbose_name="Nombre",
        help_text="Nombre de unidad",
    )
    abbreviation = models.CharField(
        "Abreviatura", max_length=10,
        unique=True,
        null=False,
        blank= False,
        help_text="Usa una abreviatura corta, p. ej., kg, m, u."
    ) 

    class Meta:
        verbose_name = "Unidad"
        verbose_name_plural = "Unidades"
        ordering = ["name"]

    def __str__(self):  
        return f"{self.name} ({self.abbreviation})"
    

class Material(models.Model):
    name = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese el nombre del material a registrar",
        verbose_name="Nombre",
        validators=[MinLengthValidator(3)]
    )
    description = models.TextField(
        max_length=200,
        null=True,
        blank=True,
        unique=False,
        help_text="Ingrese una pequeña descripción del material como referencia",
        verbose_name="Descripción",
        validators=[MinLengthValidator(3)]
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank= False,
        verbose_name="Precio",
        help_text="Ingrese el valor monetario del material",
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,   
        null=True,                   
        blank=True,                  
        related_name="material_unit",
        verbose_name="Unidad",
        help_text="Seleccione una unidad para el material"
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="material_project_catalog",
        verbose_name="Proyecto",
        help_text="Proyecto al que pertenece el material",
    )

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="uniq_material_name_per_project",
            )
        ]

    def __str__(self):
        return self.name