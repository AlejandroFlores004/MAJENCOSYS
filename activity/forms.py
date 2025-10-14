from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Activity, Header
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