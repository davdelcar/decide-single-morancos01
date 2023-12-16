from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    identifier = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Usuario o Correo Electrónico", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Contraseña", "class": "form-control"}
        )
    )

    remember_me = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )