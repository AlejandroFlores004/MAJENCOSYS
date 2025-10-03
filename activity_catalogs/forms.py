from django import forms
from .models import Unit, Material, Labour, Tool

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
