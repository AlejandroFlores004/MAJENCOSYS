from django import forms
from .models import Project
import re

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        # NOTA: excluimos 'usuario' (se toma del request) y 'estado' (solo se cambia en edición)
        fields = ["nombre", "cliente", "descripcion", "tecnico", "type", "imagen"]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Nombre del Proyecto", "class": "form-control"}),
            "cliente": forms.TextInput(attrs={"placeholder": "Nombre Completo del Cliente", "class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"placeholder": "Breve descripción del proyecto", "rows": 4, "class": "form-control"}),
            "tecnico": forms.Select(attrs={"class": "form-select"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    # --- Validaciones de negocio ---
    def clean_nombre(self):
        nombre = (self.cleaned_data.get('nombre') or '').strip()
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s\-]+", nombre):
            raise forms.ValidationError("El nombre solo puede contener letras, espacios y guiones (sin números).")
        return nombre

    def clean_cliente(self):
        cliente = (self.cleaned_data.get('cliente') or '').strip()
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s\-]+", cliente):
            raise forms.ValidationError("El cliente no puede tener números ni caracteres especiales.")
        return cliente

    def clean_descripcion(self):
        desc = (self.cleaned_data.get('descripcion') or '').strip()
        # letras, números, espacio, punto, coma y guion; al menos 10 chars
        if len(desc) < 10 or not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\s\.\,\-]+", desc):
            raise forms.ValidationError("Descripción inválida (mínimo 10 caracteres, sin símbolos raros).")
        return desc

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            if imagen.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La imagen no puede superar los 5MB.")
            if not imagen.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise forms.ValidationError("La imagen debe ser .jpg, .jpeg o .png.")
        return imagen
