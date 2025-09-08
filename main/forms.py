# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm


class UserRegistrationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        # Apply Bootstrap styling to fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingrese su dirección de correo'
        })



class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
