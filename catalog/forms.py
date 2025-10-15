from django import forms
from .models import Material,ManoObra,Herramienta,Equipo,Riesgo,Calidad,Ambiental

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

class ManoObraForm(forms.ModelForm):
    class Meta:
        model = ManoObra
        fields = ['name', 'description', 'jornada']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Maestro de obra',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escriba una breve descripción de la mano de obra...'
            }),
            'jornada': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: $40.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
        }
        labels = {
            'name': 'Nombre de la mano de obra',
            'description': 'Descripción',
            'jornada': 'Costo de jornada (USD)',
        }
        help_texts = {
            'name': 'Ingrese el nombre de la mano de obra a registrar',
            'description': 'Pequeña descripción de la mano de obra como referencia',
            'jornada': 'Valor monetario de la jornada',
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project  # <- lo inyectamos desde la vista

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name or not self.project:
            return name
        qs = ManoObra.objects.filter(project=self.project, name__iexact=name)
        # si es edición, excluir el propio registro
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe una mano de obra con ese nombre en este proyecto.")
        return name

class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = ['name', 'tipo', 'costodia']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Compactador manual',
                'required': True
            }),
            'tipo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Ligero',
                'required': True
            }),
            'costodia': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: $15.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
        }
        labels = {
            'name': 'Nombre de la herramienta',
            'tipo': 'Tipo de herramienta',
            'costodia': 'Costo por dia de uso (USD)',
        }
        help_texts = {
            'name': 'Ingrese el nombre de la herramienta a registrar',
            'tipo': 'Tipo de la herramienta a registrar',
            'costodia': 'Costo monetario de uso por dia',
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project  # <- lo inyectamos desde la vista

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name or not self.project:
            return name
        qs = Herramienta.objects.filter(project=self.project, name__iexact=name)
        # si es edición, excluir el propio registro
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe una herramienta con ese nombre en este proyecto.")
        return name

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['name', 'tipo', 'capacidad', 'costodia']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Camión volquete',
                'required': True
            }),
            'tipo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Pesado',
                'required': True
            }),
            'capacidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 0.6 m³',
                'required': True
            }),
            'costodia': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: $120.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
        }
        labels = {
            'name': 'Nombre del equipo',
            'tipo': 'Tipo del equipo',
            'capacidad': 'Capacidad del equipo',
            'costodia': 'Costo por dia de uso (USD)',
        }
        help_texts = {
            'name': 'Ingrese el nombre del equipo a registrar',
            'tipo': 'Tipo del equipo a registrar',
            'capacidad': 'Capacidad del equipo a registrar',
            'costodia': 'Costo monetario de uso por dia',
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project  # <- lo inyectamos desde la vista

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name or not self.project:
            return name
        qs = Equipo.objects.filter(project=self.project, name__iexact=name)
        # si es edición, excluir el propio registro
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un equipo con ese nombre en este proyecto.")
        return name

class RiesgoForm(forms.ModelForm):
    class Meta:
        model = Riesgo
        fields = ['name', 'peligros', 'tipo', 'nivel']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Manipulacion de herramientas',
                'required': True
            }),
            'peligros': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ejemplo: Golpes, torceduras, fracturas y cortes',
                'required': True
            }),
            'tipo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Fisico',
                'required': True
            }),
            'nivel': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Medio',
                'required': True
            }),
        }
        labels = {
            'name': 'Nombre del riesgo',
            'peligros': 'Peligros potenciales',
            'tipo': 'Tipo de riesgo',
            'nivel': 'Nivel de riesgo',
        }
        help_texts = {
            'name': 'Ingrese el nombre del riesgo a registrar',
            'peligros': 'Peligros portenciales en riesgo',
            'tipo': 'Tipo de riesgo a registrar',
            'nivel': 'Nivel de riesgo a registrar',
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project  # <- lo inyectamos desde la vista

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name or not self.project:
            return name
        qs = Riesgo.objects.filter(project=self.project, name__iexact=name)
        # si es edición, excluir el propio registro
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un riesgo con ese nombre en este proyecto.")
        return name

class CalidadForm(forms.ModelForm):
    class Meta:
        model = Calidad
        fields = ['name', 'description', 'precio', 'norma', 'tipo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Control de calidad',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escriba una breve descripción del control de calidad'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: $40.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'norma': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: ASTM, NTG, ANDA, Etc.',
                'required': True
            }),
            'tipo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Tipo de Control de calidad',
                'required': True
            }),
        }
        labels = {
            'name': 'Nombre del control de calidad',
            'description': 'Descripción',
            'precio': 'Precio de prueba (USD)',
            'norma': 'Norma del control de calidad',
            'tipo': 'Tipo del control de calidad',
        }
        help_texts = {
            'name': 'Ingrese el nombre del control de calidad a registrar',
            'description': 'Pequeña descripción del control de calidad como referencia',
            'precio': 'Valor monetario del precio',
            'name': 'Ingrese la norma del control de calidad a registrar',
            'name': 'Ingrese el tipo del control de calidad a registrar',
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project  # <- lo inyectamos desde la vista

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name or not self.project:
            return name
        qs = Calidad.objects.filter(project=self.project, name__iexact=name)
        # si es edición, excluir el propio registro
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un control de calidad con ese nombre en este proyecto.")
        return name

class AmbientalForm(forms.ModelForm):
    class Meta:
        model = Ambiental
        fields = ['name', 'description', 'epoca', 'especie', 'insumos']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Control ambiental',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escriba una breve descripción del control ambiental'
            }),
            'epoca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Verano',
                'required': True
            }),
            'especie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Roble',
                'required': True
            }),
            'insumos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ejemplo: Abono, bolsas, tierra, etc'
            }),
        }
        labels = {
            'name': 'Nombre del control ambiental',
            'description': 'Descripción del control ambiental',
            'epoca': 'Epoca del año',
            'especie': 'Especie del arbol',
            'insumos': 'Insumos necesarios',
        }
        help_texts = {
            'name': 'Ingrese el nombre del control ambiental a registrar',
            'description': 'Descripción del control ambiental a registrar',
            'epoca': 'Epoca del año a registrar',
            'especie': 'Especie del arbol a registrar',
            'insumos': 'Insumos necesarios a registrar',
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project  # <- lo inyectamos desde la vista

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name or not self.project:
            return name
        qs = Riesgo.objects.filter(project=self.project, name__iexact=name)
        # si es edición, excluir el propio registro
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un control ambiental con ese nombre en este proyecto.")
        return name
