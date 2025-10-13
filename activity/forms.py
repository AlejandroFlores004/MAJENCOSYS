from django import forms
from django.forms import inlineformset_factory
from .models import Activity, Header

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

HeaderFormSet = inlineformset_factory(
    parent_model=Activity,
    model=Header,
    form=HeaderForm,
    extra=1,
    can_delete=True,
    min_num=1,          # puedes poner 0 si quieres permitir crear sin encabezados
    validate_min=False,
    fk_name="activity",
)
