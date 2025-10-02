# forms.py
from django import forms
from django.forms import BaseInlineFormSet, ValidationError
from .models import Activity, memoryMaterial, Material, memoryLabour, Labour


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["name", "description", "unit"]
        labels = {
            "name": "Actividad",
            "description": "Descripción de la actividad",
            "unit": "Unidad de medida (m, m², m³, hr)",
        }
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
        labels = {
            "material": "Material (del proyecto)",
            "quantity": "Cantidad",
        }
        widgets = {
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Cantidad a usar (ej.: 10.00)"
            }),
            "material": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project is not None and "material" in self.fields:
            self.fields["material"].queryset = Material.objects.filter(project=project)


class BaseMemoryMaterialFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE", False):
                continue
            if form.cleaned_data.get("material") or form.cleaned_data.get("quantity"):
                count += 1
        if count < 1:
            raise ValidationError("Debes agregar al menos un material.")


class MemoryLabourForm(forms.ModelForm):
    class Meta:
        model = memoryLabour
        fields = ["labour", "prestation", "performance"]
        labels = {
            "labour": "Mano de obra",
            "prestation": "Prestación (%)",
            "performance": "Rendimiento",
        }
        widgets = {
            "labour": forms.Select(attrs={"class": "form-select"}),
            "prestation": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Prestación (0.01 - 1.00)",
                "step": "0.01", "min": "0.01", "max": "1"
            }),
            "performance": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Total jornadas (ej.: 10.00)",
                "step": "0.01", "min": "0.01"
            }),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project is not None and "labour" in self.fields:
            try:
                self.fields["labour"].queryset = Labour.objects.filter(project=project)
            except Exception:
                pass


# forms.py (solo este método corregido)
class BaseMemoryLabourFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        used_count = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE", False):
                continue

            labour = form.cleaned_data.get("labour")
            prestation = form.cleaned_data.get("prestation")
            performance = form.cleaned_data.get("performance")

            # Si empezó a llenar la fila, exige los 3 campos
            if labour or prestation is not None or performance is not None:
                used_count += 1
                if not labour:
                    # Usa el NOMBRE del campo, no el label
                    form.add_error("labour", "Este campo es obligatorio.")
                if prestation is None:
                    form.add_error("prestation", "Este campo es obligatorio.")
                if performance is None:
                    form.add_error("performance", "Este campo es obligatorio.")

        if used_count < 1:
            # Error no asociado a un campo: mínimo 1 fila
            raise ValidationError("Debes agregar al menos una mano de obra.")
