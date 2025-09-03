from django import forms  #Api de formularios
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["nombre","descripcion","estado","usuario","tecnico","type","imagen"]
        widgets = {
            "descipcion": forms.TextInput(attrs={"placeholder":"breve descripcion"}),
            
        }