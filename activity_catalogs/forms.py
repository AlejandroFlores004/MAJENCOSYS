from django import forms
from .models import Unit, Material, Labour, Tool, HeavyMachinery, QualityControl
from django.contrib.auth.models import User, Group

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["name", "abbreviation"]
        labels = {
            "name": "Nombre de la unidad",
            "abbreviation": "Abreviatura",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. Kilogramo"
            }),
            "abbreviation": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. kg"
            }),
        }


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["name", "description", "price", "unit",]
        labels = {
            "name": "Nombre del material",
            "description": "Descripción",
            "price": "Precio",
            "unit": "Unidad de medida",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. Cemento Portland"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ej. Cemento de uso general"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "Ej. 12.50"
            }),
            "unit": forms.Select(attrs={
                "class": "form-select"
            }),
        }


class LabourForm(forms.ModelForm):
    class Meta:
        model = Labour
        fields = ["name", "description", "price",]
        labels = {
            "name": "Nombre del oficio",
            "description": "Descripción",
            "price": "Valor de la jornada",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. Albañil"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ej. Mano de obra para construcción"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "Ej. 25.00"
            }),
        }


class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ["name", "dayCost",]
        labels = {
            "name": "Nombre de la herramienta o equipo",
            "dayCost": "Costo por día",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. Taladro industrial"
            }),
            "dayCost": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "Ej. 15.50"
            }),
        }


class HeavyMachineryForm(forms.ModelForm):
    class Meta:
        model = HeavyMachinery
        fields = ["name", "function", "capacity", "price"]
        labels = {
            "name": "Nombre de la maquinaria",
            "function": "Función de la maquinaria",
            "capacity": "Capacidad (opcional)",
            "price": "Precio",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. Excavadora hidráulica"
            }),
            "function": forms.Select(attrs={"class": "form-select"}),
            "capacity": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. 1.2 m³, 20 ton, 120 HP"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "Ej. 250.00"
            }),
        }

class QualityControlForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limita el combo a usuarios del grupo "Supervisor"
        try:
            supervisor_group = Group.objects.get(name="Supervisor")
            self.fields["responsible"].queryset = User.objects.filter(groups=supervisor_group).order_by("first_name", "last_name", "username")
        except Group.DoesNotExist:
            # Si no existe el grupo aún, deja vacío para evitar confusiones
            self.fields["responsible"].queryset = User.objects.none()

    class Meta:
        model = QualityControl
        fields = ["name", "description", "responsible"]
        labels = {
            "name": "Nombre de la prueba",
            "description": "Descripción de la prueba",
            "responsible": "Responsable (Supervisor)",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. Ensayo de slump (asentamiento)"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Objetivo, método, criterios de aceptación…"
            }),
            "responsible": forms.Select(attrs={"class": "form-select"}),
        }
