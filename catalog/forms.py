from django import forms
from .models import Material

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'description', 'price', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Cemento gris tipo IP',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escriba una breve descripción del material...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 8.50',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
        }
        labels = {
            'name': 'Nombre del Material',
            'description': 'Descripción',
            'price': 'Precio (USD)',
            'unit': 'Unidad',
        }
        help_texts = {
            'name': 'Ingrese el nombre del material a registrar',
            'description': 'Pequeña descripción del material como referencia',
            'price': 'Valor monetario del material',
            'unit': 'Seleccione la unidad correspondiente',
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project  # <- lo inyectamos desde la vista

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name or not self.project:
            return name
        qs = Material.objects.filter(project=self.project, name__iexact=name)
        # si es edición, excluir el propio registro
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un material con ese nombre en este proyecto.")
        return name
