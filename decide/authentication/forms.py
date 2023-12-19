from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    identifier = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": _("Usuario o Correo Electrónico"), "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": _("Contraseña"), "class": "form-control"}
        )
    )

    remember_me = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": _("Correo electrónico"), "class": "form-control"}
        )
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": _("Nombre de usuario"), "class": "form-control"}
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": _("Contraseña"), "class": "form-control"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": _("Confirmar contraseña"), "class": "form-control"}
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": _("Nombre"), "class": "form-control"}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": _("Apellidos"), "class": "form-control"}
        )
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("El correo electrónico ya está en uso"))
        return email

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "first_name", "last_name")