from django import forms
from .models import ReportTemplate

class ReportTemplateForm(forms.ModelForm):
    """Solo el nombre; el payload (columns/filters/order/group_by) viene como JSON oculto."""
    class Meta:
        model = ReportTemplate
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class":"form-control","placeholder":"Nombre del reporte"})
        }
