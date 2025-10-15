from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Activity, Header, MemoryMaterial, MemoryManoObra, MemoryHerramienta, MemoryEquipo
from catalog.models import Material, ManoObra, Herramienta, Equipo
from django.core.exceptions import ValidationError

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de la actividad",
                    "autofocus": "autofocus",
                }
            )
        }
        help_texts = {
            "name": "Ingrese el nombre de la actividad (único dentro del proyecto)."
        }

class HeaderForm(forms.ModelForm):
    class Meta:
        model = Header
        fields = ["name", "content"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del encabezado"}
            ),
            "content": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Contenido"}
            ),
        }

class BaseHeaderFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        seen = {}  # key -> form que lo tuvo primero
        for form in self.forms:
            if not getattr(form, "cleaned_data", None):
                continue
            if form.cleaned_data.get("DELETE"):
                continue

            name = form.cleaned_data.get("name")
            if not name:
                continue

            key = name.strip().lower()
            if key in seen:
                # Marca error solo en el campo del duplicado actual
                form.add_error("name", "Ya existe otro encabezado con este nombre en esta actividad.")
                # Si quieres, también puedes marcar el primero:
                # seen[key].add_error("name", "Nombre duplicado con otra fila.")
            else:
                seen[key] = form

HeaderFormSet = inlineformset_factory(
    parent_model=Activity,
    model=Header,
    form=HeaderForm,
    formset=BaseHeaderFormSet,   # <-- usa el formset con clean()
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=False,
    fk_name="activity",
)

class MemoryMaterialForm(forms.ModelForm):
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = project  # lo guardamos para validar en clean
        if project is not None:
            self.fields["material"].queryset = Material.objects.filter(project=project)

    def clean(self):
        cleaned = super().clean()
        material = cleaned.get("material")
        if material and self._project and material.project_id != self._project.id:
            # Blindaje por si manipulan el POST
            self.add_error("material", "El material no pertenece al proyecto seleccionado.")
        return cleaned

    class Meta:
        model = MemoryMaterial
        fields = ("material", "quantity")
        widgets = {
            "material": forms.Select(attrs={"class": "form-select form-select-sm w-100"}),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control form-control-sm w-100", "step": "0.01", "min": "0.01"
            }),
        }

MemoryMaterialFormSet = inlineformset_factory(
    Activity,
    MemoryMaterial,
    form=MemoryMaterialForm,
    fields=("material", "quantity"),
    extra=0,             # 1 fila en blanco por defecto
    can_delete=True,     # permitir eliminar filas existentes
    validate_min=False,
    validate_max=False,
)

class MemoryManoObraForm(forms.ModelForm):
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = project  # guardamos el proyecto para validación posterior
        if project is not None:
            self.fields["manoobra"].queryset = ManoObra.objects.filter(project=project)

    def clean(self):
        cleaned = super().clean()
        manoobra = cleaned.get("manoobra")

        if manoobra and self._project and manoobra.project_id != self._project.id:
            # Validación extra contra manipulación del POST
            self.add_error("manoobra", "La mano de obra no pertenece al proyecto seleccionado.")

        return cleaned

    class Meta:
        model = MemoryManoObra
        fields = ("manoobra", "prestaciones", "rendimiento")
        widgets = {
            "manoobra": forms.Select(attrs={"class": "form-select form-select-sm w-100"}),
            "prestaciones": forms.NumberInput(attrs={
                "class": "form-control form-control-sm w-100",
                "step": "0.01",
                "min": "0.01"
            }),
            "rendimiento": forms.NumberInput(attrs={
                "class": "form-control form-control-sm w-100",
                "step": "0.01",
                "min": "0.01"
            }),
        }

MemoryManoObraFormSet = inlineformset_factory(
    Activity,
    MemoryManoObra,
    form=MemoryManoObraForm,
    fields=("manoobra", "prestaciones", "rendimiento"),
    extra=0,            # Sin filas vacías por defecto
    can_delete=True,    # Permitir eliminar registros existentes
    validate_min=False,
    validate_max=False,
)

class MemoryHerramientaForm(forms.ModelForm):
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = project  # lo guardamos para validación en clean
        if project is not None:
            # Limita las herramientas al proyecto actual
            self.fields["herramienta"].queryset = Herramienta.objects.filter(project=project)

    def clean(self):
        cleaned = super().clean()
        herramienta = cleaned.get("herramienta")

        # Blindaje por si manipulan el POST
        if herramienta and self._project and getattr(herramienta, "project_id", None) != self._project.id:
            self.add_error("herramienta", "La herramienta no pertenece al proyecto seleccionado.")

        return cleaned

    class Meta:
        model = MemoryHerramienta
        fields = ("herramienta", "rendimiento")
        widgets = {
            "herramienta": forms.Select(attrs={"class": "form-select form-select-sm w-100"}),
            "rendimiento": forms.NumberInput(attrs={
                "class": "form-control form-control-sm w-100",
                "step": "0.01",
                "min": "0.01",
            }),
        }

MemoryHerramientaFormSet = inlineformset_factory(
    parent_model=Activity,
    model=MemoryHerramienta,
    form=MemoryHerramientaForm,
    fields=("herramienta", "rendimiento"),
    extra=0,          # sin filas en blanco por defecto
    can_delete=True,  # permitir eliminar filas existentes
    validate_min=False,
    validate_max=False,
)

class MemoryEquipoForm(forms.ModelForm):
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = project  # guardamos el proyecto actual para validaciones
        if project is not None:
            # Filtramos solo los equipos asociados al proyecto actual
            self.fields["equipo"].queryset = Equipo.objects.filter(project=project)

    def clean(self):
        cleaned = super().clean()
        equipo = cleaned.get("equipo")

        # Validación extra contra manipulación de datos
        if equipo and self._project and getattr(equipo, "project_id", None) != self._project.id:
            self.add_error("equipo", "El equipo no pertenece al proyecto seleccionado.")

        return cleaned

    class Meta:
        model = MemoryEquipo
        fields = ("equipo", "rendimiento")
        widgets = {
            "equipo": forms.Select(attrs={"class": "form-select form-select-sm w-100"}),
            "rendimiento": forms.NumberInput(attrs={
                "class": "form-control form-control-sm w-100",
                "step": "0.01",
                "min": "0.01",
            }),
        }

MemoryEquipoFormSet = inlineformset_factory(
    parent_model=Activity,
    model=MemoryEquipo,
    form=MemoryEquipoForm,
    fields=("equipo", "rendimiento"),
    extra=0,           # sin filas vacías por defecto
    can_delete=True,   # permite eliminar registros existentes
    validate_min=False,
    validate_max=False,
)

