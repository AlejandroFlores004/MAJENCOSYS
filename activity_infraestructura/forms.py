# forms.py
from django import forms
from django.forms import BaseInlineFormSet, ValidationError  # 👈 importa ValidationError
from .models import Activity, memoryMaterial, Material

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["name", "description", "unit"]
        widgets = {
            "name": forms.TextInput(attrs={"class":"form-control","placeholder":"Ingrese el nombre de la actividad"}),
            "description": forms.Textarea(attrs={"class":"form-control","placeholder":"Ingrese la descripción","rows":4}),
            "unit": forms.TextInput(attrs={"class":"form-control","placeholder":"Ingrese la unidad de la actividad (ej.: m, m², m³, hr)"}),
        }

class MemoryMaterialForm(forms.ModelForm):
    class Meta:
        model = memoryMaterial
        fields = ["quantity", "material"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"class":"form-control","placeholder":"Cantidad a usar (ej.: 10.00)"}),
            "material": forms.Select(attrs={"class":"form-select"}),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra materiales por proyecto si corresponde
        if project is not None:
            self.fields["material"].queryset = Material.objects.filter(project=project)

class BaseMemoryMaterialFormSet(BaseInlineFormSet):
    """
    - Valida que exista al menos 1 fila 'real' (no eliminada).
    - No es necesario recibir 'project' aquí si pasamos form_kwargs desde la vista.
      (lo dejo simple para evitar duplicar lógicas).
    """
    def clean(self):
        super().clean()

        valid_rows = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE", False):
                continue

            # Cuenta la fila si tiene datos relevantes (puedes exigir ambos campos si quieres)
            has_material = form.cleaned_data.get("material")
            has_quantity = form.cleaned_data.get("quantity")
            if has_material or has_quantity:
                valid_rows += 1

        if valid_rows < 1:
            raise ValidationError("Debes agregar al menos un material.")
