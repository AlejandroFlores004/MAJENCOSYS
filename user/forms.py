from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class userForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    # campo singular para elegir solo un grupo
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label='Rol'
    )
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # aseguramos estilo Bootstrap en todos los campos (incluyendo password1 y password2)
        for name, field in self.fields.items():
            if name == 'group':  # ya tiene 'form-select'
                continue
            css_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css_class + ' form-control').strip()
            # opcional: usar el label como placeholder si no tiene
            if not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = field.label
    def save(self, commit=True):
        user = super().save(commit)  # crea el usuario
        group = self.cleaned_data.get('group')
        if group:
            user.groups.set([group])  # asigna el grupo único
        return user


class UserUpdateForm(forms.ModelForm):
    # single select
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label='Rol',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')  # no passwords

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap on text inputs
        for name in ('username', 'first_name', 'last_name', 'email'):
            self.fields[name].widget.attrs.setdefault('class', 'form-control')
            self.fields[name].widget.attrs.setdefault('placeholder', self.fields[name].label)
        # NOTE: no initial for `group` on purpose

    def save(self, commit=True):
        user = super().save(commit)
        # set exactly ONE group (replace any existing ones)
        grp = self.cleaned_data['group']
        user.groups.set([grp])
        return user