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
        return f"{self.name} (${self.price}) c/{ self.unit.abbreviation if self.unit else 'sin unidad' }"
    
class ManoObra(models.Model):
    name = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese el nombre de la mano de obra",
        verbose_name="Nombre_mo",
        validators=[MinLengthValidator(3)]
    )
    description = models.TextField(
        max_length=200,
        null=True,
        blank=True,
        unique=False,
        help_text="Ingrese una pequeña descripción de la mano de obra",
        verbose_name="Descripción_mo",
        validators=[MinLengthValidator(3)]
    )
    jornada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank= False,
        verbose_name="Jornada",
        help_text="Ingrese el valor monetario de la jornada",
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="manoobra_project_catalog",
        verbose_name="Proyecto_mo",
        help_text="Proyecto al que pertenece el material",
    )

    class Meta:
        verbose_name = "Mano de Obra"
        verbose_name_plural = "Manos de Obra"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="manoobra_name_jorn_project",
            )
        ]

    def __str__(self):
        return self.name
    
class Herramienta(models.Model):
    name = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese el nombre de la herramienta",
        verbose_name="Nombre_hrr",
        validators=[MinLengthValidator(3)]
    )
    tipo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Ingrese el tipo de la herramienta",
        verbose_name="Tipo_hrr",
        validators=[MinLengthValidator(3)]
    )
    costodia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank= False,
        verbose_name="CostoDia_hrr",
        help_text="Ingrese el costo por dia",
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="herramienta_project_catalog",
        verbose_name="Proyecto_hrr",
        help_text="Proyecto al que pertenece la herramienta",
    )

    class Meta:
        verbose_name = "Herramienta"
        verbose_name_plural = "Herramientas"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="herramienta_project",
            )
        ]

    def __str__(self):
        return self.name
     
class Equipo(models.Model):
    name = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese el nombre del equipo",
        verbose_name="Nombre_eqp",
        validators=[MinLengthValidator(3)]
    )
    tipo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Ingrese el tipo del equipo",
        verbose_name="Tipo_eqp",
        validators=[MinLengthValidator(3)]
    )
    capacidad = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Ingrese la capacidad del equipo",
        verbose_name="Capac_eqp",
        validators=[MinLengthValidator(3)]
    )
    costodia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank= False,
        verbose_name="CostoDia_eqp",
        help_text="Ingrese el costo por dia",
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="equipo_project_catalog",
        verbose_name="Proyecto_eqp",
        help_text="Proyecto al que pertenece el equipo",
    )

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="equipo_project",
            )
        ]

    def __str__(self):
        return self.name
    
class Riesgo(models.Model):
    name = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese el nombre del riesgo a registrar",
        verbose_name="Nombre_rsg",
        validators=[MinLengthValidator(3)]
    )
    peligros = models.TextField(
        max_length=200,
        null=True,
        blank=True,
        unique=False,
        help_text="Ingrese una pequeña descripción de lo peligros del riesgo",
        verbose_name="Peligros_rsg",
        validators=[MinLengthValidator(3)]
    )
    tipo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Ingrese el tipo de riesgo",
        verbose_name="Tipo_rsg",
        validators=[MinLengthValidator(3)]
    )
    nivel = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Ingrese el nivel de riesgo",
        verbose_name="Nivel_rsg",
        validators=[MinLengthValidator(3)]
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="riesgo_project_catalog",
        verbose_name="Proyecto",
        help_text="Proyecto al que pertenece el riesgo",
    )

    class Meta:
        verbose_name = "Riesgo"
        verbose_name_plural = "Riesgos"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="riesgo_project",
            )
        ]

    def __str__(self):
        return self.name
    
class Calidad(models.Model):
    name = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese el nombre del control de calidad",
        verbose_name="Nombre_cld",
        validators=[MinLengthValidator(3)]
    )
    description = models.TextField(
        max_length=200,
        null=True,
        blank=True,
        unique=False,
        help_text="Ingrese una pequeña descripción del control de calidad",
        verbose_name="Descripción_cld",
        validators=[MinLengthValidator(3)]
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank= False,
        verbose_name="Precio_cld",
        help_text="Ingrese el valor monetario del control de calidad",
    )
    norma = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese la norma del control de calidad",
        verbose_name="Norma_cld",
        validators=[MinLengthValidator(3)]
    )
    tipo = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese el tipo del control de calidad",
        verbose_name="Tipo_cld",
        validators=[MinLengthValidator(3)]
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="calidad_project_catalog",
        verbose_name="Proyecto_cld",
        help_text="Proyecto al que pertenece el control de calidad",
    )

    class Meta:
        verbose_name = "Calidad"
        verbose_name_plural = "Calidades"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="calidad_project",
            )
        ]

    def __str__(self):
        return self.name
    
class Ambiental(models.Model):
    name = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese el nombre del control ambiental a registrar",
        verbose_name="Nombre_mbt",
        validators=[MinLengthValidator(3)]
    )
    description = models.TextField(
        max_length=200,
        null=True,
        blank=True,
        unique=False,
        help_text="Ingrese una pequeña descripción del control ambiental",
        verbose_name="Descripción_mbt",
        validators=[MinLengthValidator(3)]
    )
    epoca = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Ingrese la epoca del año",
        verbose_name="Epoca_mbt",
        validators=[MinLengthValidator(3)]
    )
    especie = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Ingrese la especide de las plantas",
        verbose_name="Especie_mbt",
        validators=[MinLengthValidator(3)]
    )
    insumos = models.TextField(
        max_length=200,
        null=True,
        blank=True,
        unique=False,
        help_text="Ingrese una pequeña descripción de los insumos",
        verbose_name="Insumos_mbt",
        validators=[MinLengthValidator(3)]
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="ambiental_project_catalog",
        verbose_name="Proyecto_mbt",
        help_text="Proyecto al que pertenece el control ambiental",
    )

    class Meta:
        verbose_name = "Ambiental"
        verbose_name_plural = "Ambientals"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="ambiental_project",
            )
        ]

    def __str__(self):
        return self.name
    
class Hidrologica(models.Model):
    name = models.CharField(
        max_length=100, 
        null=False, 
        blank=False,
        help_text="Ingrese el nombre de la prueba hidrologica a registrar",
        verbose_name="Nombre_hdg",
        validators=[MinLengthValidator(3)]
    )
    description = models.TextField(
        max_length=200,
        null=True,
        blank=True,
        unique=False,
        help_text="Ingrese una pequeña descripción de la prueba hidrologica",
        verbose_name="Descripción_hdg",
        validators=[MinLengthValidator(3)]
    )
    ubicacion = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Ingrese el tipo de ubicacion de la prueba hidrologica",
        verbose_name="Ubicacion_hdg",
        validators=[MinLengthValidator(3)]
    )
    parametro = models.TextField(
        max_length=200,
        null=True,
        blank=True,
        unique=False,
        help_text="Ingrese los parametros de la prueba hidrologica",
        verbose_name="Parametro_hdg",
        validators=[MinLengthValidator(3)]
    )
    unidad = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Ingrese la unidad de la prueba hidrologica",
        verbose_name="Unidad_hdg",
        validators=[MinLengthValidator(3)]
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="hidrologica_project_catalog",
        verbose_name="Proyecto_hdg",
        help_text="Proyecto al que pertenece la prueba hidrologica",
    )

    class Meta:
        verbose_name = "Hidrologica"
        verbose_name_plural = "Hidrologicas"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="hidrologica_project",
            )
        ]

    def __str__(self):
        return self.name
    