from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Activity, Header, MemoryMaterial, MemoryManoObra, MemoryHerramienta, MemoryEquipo, MemoryRiesgos, MemoryCalidad, MemoryAmbiental, MemoryHidrologica
from catalog.models import Material, ManoObra, Herramienta, Equipo, Riesgo, Calidad, Ambiental, Hidrologica
from project.models import Project
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

class MemoryRiesgosForm(forms.ModelForm):
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = project  # lo usamos para filtrar y validar
        # Filtra riesgos por proyecto si aplica
        if project is not None and hasattr(Riesgo, "project_id"):
            self.fields["riesgo"].queryset = Riesgo.objects.filter(project=project)

        # Opcional: placeholders
        self.fields["medida"].widget.attrs.update({"placeholder": "Ej. Señalización, EPP, barreras..."})
        self.fields["descripcion_medida"].widget.attrs.update({"placeholder": "Descripción breve de la medida"})
        self.fields["costo"].widget.attrs.update({"placeholder": "0.00"})

    def clean(self):
        cleaned = super().clean()
        riesgo = cleaned.get("riesgo")

        # Blindaje por manipulación del POST: riesgo debe pertenecer al proyecto
        if riesgo and self._project and hasattr(riesgo, "project_id"):
            if riesgo.project_id != self._project.id:
                self.add_error("riesgo", "El riesgo no pertenece al proyecto seleccionado.")

        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        # Asegurar que el registro quede amarrado al proyecto actual
        if self._project:
            obj.project = self._project
        if commit:
            obj.save()
        return obj

    class Meta:
        model = MemoryRiesgos
        # activity y project no se editan aquí (activity lo pone el inline, project lo fijamos en save)
        fields = ("riesgo", "medida", "descripcion_medida", "costo")
        widgets = {
            "riesgo": forms.Select(attrs={"class": "form-select form-select-sm w-100"}),
            "medida": forms.TextInput(attrs={"class": "form-control form-control-sm w-100"}),
            "descripcion_medida": forms.Textarea(attrs={
                "class": "form-control form-control-sm w-100",
                "rows": 2,
            }),
            "costo": forms.NumberInput(attrs={
                "class": "form-control form-control-sm w-100",
                "step": "0.01",
                "min": "0.00",
            }),
        }

MemoryRiesgosFormSet = inlineformset_factory(
    parent_model=Activity,
    model=MemoryRiesgos,
    form=MemoryRiesgosForm,
    fields=("riesgo", "medida", "descripcion_medida", "costo"),
    extra=0,          # sin filas en blanco por defecto (ajusta si quieres)
    can_delete=True,  # permitir eliminar filas
    validate_min=False,
    validate_max=False,
)

class MemoryCalidadForm(forms.ModelForm):
    def __init__(self, *args, project: Project = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = project  # guardamos el proyecto actual
        if project is not None and hasattr(Calidad, "project_id"):
            # Filtrar los controles de calidad que pertenecen al proyecto
            self.fields["calidad"].queryset = Calidad.objects.filter(project=project)

        # Agregar placeholders y clases visuales coherentes
        self.fields["responsable"].widget.attrs.update({"placeholder": "Nombre del responsable"})
        self.fields["cantidad"].widget.attrs.update({"placeholder": "1"})

    def clean(self):
        cleaned = super().clean()
        calidad = cleaned.get("calidad")

        # Validar que el control de calidad pertenezca al proyecto correcto
        if calidad and self._project and hasattr(calidad, "project_id"):
            if calidad.project_id != self._project.id:
                self.add_error("calidad", "El control de calidad no pertenece al proyecto seleccionado.")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self._project:
            obj.project = self._project  # Asignar proyecto antes de guardar
        if commit:
            obj.save()
        return obj

    class Meta:
        model = MemoryCalidad
        fields = ("calidad", "cantidad", "responsable")
        widgets = {
            "calidad": forms.Select(attrs={"class": "form-select form-select-sm w-100"}),
            "cantidad": forms.NumberInput(attrs={
                "class": "form-control form-control-sm w-100",
                "min": "1",
                "step": "1",
            }),
            "responsable": forms.TextInput(attrs={
                "class": "form-control form-control-sm w-100",
            }),
        }

MemoryCalidadFormSet = inlineformset_factory(
    parent_model=Activity,
    model=MemoryCalidad,
    form=MemoryCalidadForm,
    fields=("calidad", "cantidad", "responsable"),
    extra=0,           # sin filas en blanco por defecto
    can_delete=True,   # permitir eliminar registros
    validate_min=False,
    validate_max=False,
)


class MemoryAmbientalForm(forms.ModelForm):
    def __init__(self, *args, project: Project = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = project
        if project is not None and hasattr(Ambiental, "project_id"):
            # Limita los controles ambientales al proyecto actual (si Ambiental tiene project)
            self.fields["ambiental"].queryset = Ambiental.objects.filter(project=project)

        # UX: placeholders
        self.fields["valor"].widget.attrs.update({"placeholder": "0.00"})

    def clean(self):
        cleaned = super().clean()
        ambiental = cleaned.get("ambiental")

        # Blindaje: el control ambiental debe pertenecer al proyecto
        if ambiental and self._project and hasattr(ambiental, "project_id"):
            if ambiental.project_id != self._project.id:
                self.add_error("ambiental", "El control ambiental no pertenece al proyecto seleccionado.")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self._project:
            obj.project = self._project  # asegurar vínculo al proyecto actual
        if commit:
            obj.save()
        return obj

    class Meta:
        model = MemoryAmbiental
        fields = ("ambiental", "valor")
        widgets = {
            "ambiental": forms.Select(attrs={"class": "form-select form-select-sm w-100"}),
            "valor": forms.NumberInput(attrs={
                "class": "form-control form-control-sm w-100",
                "step": "0.01",
                "min": "0.01",
            }),
        }


MemoryAmbientalFormSet = inlineformset_factory(
    parent_model=Activity,
    model=MemoryAmbiental,
    form=MemoryAmbientalForm,
    fields=("ambiental", "valor"),
    extra=0,          # sin filas en blanco por defecto
    can_delete=True,  # permitir eliminar registros
    validate_min=False,
    validate_max=False,
)

class MemoryHidrologicaForm(forms.ModelForm):
    def __init__(self, *args, project: Project = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = project

        # Si el modelo Hidrologica tiene campo project, filtramos
        if project is not None and hasattr(Hidrologica, "project_id"):
            self.fields["hidrologica"].queryset = Hidrologica.objects.filter(project=project)

        # Mejora UX
        self.fields["costo"].widget.attrs.update({
            "placeholder": "0.00",
            "min": "0.01",
            "step": "0.01",
        })

    def clean(self):
        cleaned = super().clean()
        hidrologica = cleaned.get("hidrologica")

        # Validación de pertenencia al proyecto
        if hidrologica and self._project and hasattr(hidrologica, "project_id"):
            if hidrologica.project_id != self._project.id:
                self.add_error("hidrologica", "La prueba hidrológica no pertenece al proyecto seleccionado.")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self._project:
            obj.project = self._project  # aseguramos vínculo con el proyecto actual
        if commit:
            obj.save()
        return obj

    class Meta:
        model = MemoryHidrologica
        fields = ("hidrologica", "costo")
        widgets = {
            "hidrologica": forms.Select(attrs={
                "class": "form-select form-select-sm w-100",
            }),
            "costo": forms.NumberInput(attrs={
                "class": "form-control form-control-sm w-100",
                "step": "0.01",
                "min": "0.01",
            }),
        }


MemoryHidrologicaFormSet = inlineformset_factory(
    parent_model=Activity,
    model=MemoryHidrologica,
    form=MemoryHidrologicaForm,
    fields=("hidrologica", "costo"),
    extra=0,          # sin filas extra
    can_delete=True,  # permitir eliminar
    validate_min=False,
    validate_max=False,
)