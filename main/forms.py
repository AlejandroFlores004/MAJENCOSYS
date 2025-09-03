# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    # You can add custom fields here if needed, but AuthenticationForm already includes fields for username and password
    pass
