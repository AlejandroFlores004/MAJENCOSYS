# project/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from .models import Project
import re
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import ClearableFileInput
from django.conf import settings
from django.contrib.auth import get_user_model

ALLOWED_IMAGE_TYPES = ("image/jpeg", "image/png", "image/webp")

# Widget para permitir selección múltiple en <input type="file">
class MultiFileInput(ClearableFileInput):           # heredamos del ClearableFileInput estándar
    allow_multiple_selected = True                  # <-- habilita multiple=True

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["nombre", "cliente", "tecnico", "type", "imagen", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Digite el Nombre del Proyecto",
                "maxlength": 150,
            }),
            "cliente": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Digite el Nombre Completo del Cliente",
                "maxlength": 150,
            }),
            "tecnico": forms.Select(attrs={"class": "form-select"}),
            "imagen": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Breve descripción del proyecto",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # FK técnico
        fk_model = Project._meta.get_field("tecnico").remote_field.model
        self.fields["tecnico"].queryset = fk_model.objects.all().order_by("id")

        # Choices de tipo (con "---------")
        type_field = Project._meta.get_field("type")
        self.fields["type"] = forms.ChoiceField(
            choices=[("", "---------")] + list(type_field.choices),
            required=True,
            widget=forms.Select(attrs={"class": "form-select"}),
            label="Tipo de Proyecto",
        )

        # El widget no obliga; la regla va en clean()
        self.fields["imagen"].required = False

    # ===== Validaciones de contenido =====
    _re_nombre_cliente = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s\-]+$")
    _re_descripcion = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\s\.,\-]+$")

    def clean_nombre(self):
        v = (self.cleaned_data.get("nombre") or "").strip()
        if not v or not self._re_nombre_cliente.fullmatch(v):
            raise ValidationError("El nombre solo puede contener letras, espacios y guiones (sin números).")
        return v

    def clean_cliente(self):
        v = (self.cleaned_data.get("cliente") or "").strip()
        if not v or not self._re_nombre_cliente.fullmatch(v):
            raise ValidationError("El cliente solo puede contener letras, espacios y guiones (sin números).")
        return v

    def clean_descripcion(self):
        v = (self.cleaned_data.get("descripcion") or "").strip()
        if len(v) < 10:
            raise ValidationError("La descripción debe tener al menos 10 caracteres.")
        if not self._re_descripcion.fullmatch(v):
            raise ValidationError("La descripción no puede contener caracteres especiales (solo punto, coma y guion).")
        return v

    def clean_imagen(self):
        """
        Valida SOLO si viene un archivo subido (UploadedFile).
        Si el form se está editando sin subir nada, se deja tal cual.
        """
        f = self.cleaned_data.get("imagen")
        if not f:
            return f

        # Solo validar si es un archivo nuevo (subido)
        if not isinstance(f, UploadedFile):
            return f

        ctype = getattr(f, "content_type", None)
        if ctype and ctype not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("La imagen debe ser JPG, PNG o WEBP.")
        if getattr(f, "size", 0) > 5 * 1024 * 1024:
            raise ValidationError("La imagen no debe superar 5 MB.")
        return f

    def clean(self):
        """
        Regla de negocio:
        - Creación: siempre debe haber imagen subida.
        - Edición:
            * Si el proyecto ya tiene imagen, puedes guardar sin subir otra (se conserva).
            * Si NO tiene imagen (o el archivo no existe en disco), debes subir una.
        """
        cleaned = super().clean()
        new_file = cleaned.get("imagen")

        creating = not (self.instance and self.instance.pk)
        has_current = False
        if self.instance and self.instance.imagen:
            try:
                has_current = default_storage.exists(self.instance.imagen.name)
            except Exception:
                has_current = False

        if creating:
            if not isinstance(new_file, UploadedFile):
                raise ValidationError({"imagen": "Debes seleccionar una imagen para el proyecto."})
        else:
            # Editando
            if not has_current and not isinstance(new_file, UploadedFile):
                raise ValidationError({"imagen": "El proyecto debe tener una imagen (sube una)."})
        return cleaned

    def save(self, commit=True):
        """
        Reemplazo: si suben archivo nuevo, guarda y borra el anterior.
        """
        instance = super().save(commit=False)

        new_file = self.cleaned_data.get("imagen")
        old_path = None
        if instance.pk:
            try:
                old = Project.objects.get(pk=instance.pk)
                if old.imagen:
                    old_path = old.imagen.name
            except Project.DoesNotExist:
                pass

        if commit:
            instance.save()
            self.save_m2m()

            # Si subieron un archivo nuevo, borro el anterior (si es otro)
            if isinstance(new_file, UploadedFile) and old_path and instance.imagen and old_path != instance.imagen.name:
                try:
                    if default_storage.exists(old_path):
                        default_storage.delete(old_path)
                except Exception:
                    pass

        return instance

#Crud Carda de Archivos Tecnicos

# ---------- Config (overridable por settings) ----------
def _allowed_exts():
    return getattr(settings, "ALLOWED_FILE_EXTS",
                   ["pdf", "dwg", "docx", "xlsx", "mp4", "bak", "jpg", "jpeg", "png"])

def _max_upload_mb():
    return int(getattr(settings, "MAX_UPLOAD_MB", 100))  # MB por archivo

def _bytes_limit():
    return _max_upload_mb() * 1024 * 1024

def _max_files_per_upload():
    return getattr(settings, "MAX_FILES_PER_UPLOAD", 50)  # por lote

# ---------- Widget <input type=file multiple> ----------
class MultiFileInput(forms.FileInput):
    allow_multiple_selected = True
    def __init__(self, attrs=None):
        base = {"class": "form-control", "multiple": True}
        attrs = {**base, **(attrs or {})}
        super().__init__(attrs=attrs)
    def value_from_datadict(self, data, files, name):
        return files.getlist(name)  # siempre lista

# ---------- Field para lista con validación por lote ----------
class MultiFileField(forms.Field):
    widget = MultiFileInput
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)
    def clean(self, data):
        files = data or []
        if not files:
            raise ValidationError(_("Debes seleccionar al menos un archivo."))
        max_files = _max_files_per_upload()
        if isinstance(max_files, int) and max_files > 0 and len(files) > max_files:
            raise ValidationError(_("Máximo %(n)s archivos por subida."), params={"n": max_files})
        for f in files:
            size = int(getattr(f, "size", 0) or 0)
            if size <= 0:
                raise ValidationError(_("Uno de los archivos está vacío o es ilegible."))
            if size > _bytes_limit():
                raise ValidationError(_("Un archivo supera %(mb)s MB."), params={"mb": _max_upload_mb()})
            name = getattr(f, "name", "")
            ext = (name.rsplit(".", 1)[-1] if "." in name else "").lower()
            if ext not in _allowed_exts():
                raise ValidationError(_("Extensión no permitida: .%(ext)s"), params={"ext": ext})
        return files

# ---------- Form de subida múltiple ----------
class ArchivoTecnicoUploadForm(forms.Form):
    archivos = MultiFileField(label=_("Seleccionar archivos"))
    descripcion = forms.CharField(
        label=_("Descripción (opcional)"), required=False,
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control",
                                     "placeholder": _("Descripción (opcional)")})
    )

# ---------- Form de filtros del listado ----------
FILE_TYPE_CHOICES = (
    ("", "Todos"),
    ("img", "Imágenes"),
    ("pdf", "PDF"),
    ("doc", "Office"),
    ("dwg", "CAD"),
    ("video", "Video"),
    ("bak", "Backups"),
    ("otros", "Otros"),
)

class ArchivoTecnicoFilterForm(forms.Form):
    q = forms.CharField(
        label=_("Nombre o descripción"), required=False,
        widget=forms.TextInput(attrs={"class": "form-control",
                                      "placeholder": _("Nombre o descripción")}),
    )
    tipo = forms.ChoiceField(
        label=_("Tipo"), required=False, choices=FILE_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    usuario = forms.ChoiceField(
        label=_("Subido por"), required=False, choices=[("", "Todos")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    fecha_desde = forms.DateField(
        label=_("Desde"), required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    fecha_hasta = forms.DateField(
        label=_("Hasta"), required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar combo de usuarios (ordenado)
        User = get_user_model()
        self.fields["usuario"].choices = [("", "Todos")] + [
            (u.id, getattr(u, "username", str(u))) for u in User.objects.order_by("username")
        ]

    def clean(self):
        data = super().clean()
        d1, d2 = data.get("fecha_desde"), data.get("fecha_hasta")
        if d1 and d2 and d1 > d2:
            raise ValidationError(_("Rango de fechas inválido."))
        return data