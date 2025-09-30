# forms.py
from django import forms
from .models import Activity, memoryMaterial, Material

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["name", "description", "unit"]  # unit is CharField in your model
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese el nombre de la actividad"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Ingrese la descripción",
                "rows": 4
            }),
            "unit": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese la unidad de la actividad (ej.: m, m², m³, hr)"
            }),
        }

class MemoryMaterialForm(forms.ModelForm):
    class Meta:
        model = memoryMaterial
        fields = ["quantity", "material"]
        widgets = {
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Cantidad a usar (ej.: 10.00)"
            }),
            "material": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Si tu modelo Material tiene FK a Project, filtra por el proyecto actual:
        if project is not None:
            self.fields["material"].queryset = Material.objects.filter(project=project)
        # Si no tienes esa FK, elimina el bloque anterior.
