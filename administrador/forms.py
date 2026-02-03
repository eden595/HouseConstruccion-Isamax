from django import forms
from django.contrib.auth.models import User


class UsuarioCrearForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Contraseña"}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Repite la contraseña"}),
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "is_active": "Activo",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Nombre de usuario"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Nombre"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Apellido"}),
            "email": forms.EmailInput(attrs={"placeholder": "correo@dominio.com"}),
            "is_active": forms.CheckboxInput(),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        if p1 and len(p1) < 8:
            self.add_error("password1", "La contraseña debe tener al menos 8 caracteres.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UsuarioEditarForm(forms.ModelForm):
    """
    Formulario para editar datos básicos del usuario (sin cambiar contraseña).
    """

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "is_active": "Activo",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Nombre de usuario"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Nombre"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Apellido"}),
            "email": forms.EmailInput(attrs={"placeholder": "correo@dominio.com"}),
            "is_active": forms.CheckboxInput(),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        qs = User.objects.filter(username=username).exclude(pk=self.instance.pk if self.instance else None)
        if qs.exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre.")
        return username
