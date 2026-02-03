from django import forms
from .models import Pais, Ciudad, Estado

class PaisForm(forms.ModelForm):
    class Meta:
        model = Pais
        fields = ['nombre', 'fecha_creacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nombre del País'}),
            "fecha_creacion": forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control form-control-sm', 'readonly': 'readonly'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return nombre.title()

class CiudadForm(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = ['pais', 'nombre', 'fecha_creacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nombre de la Ciudad'}),
            'pais': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            "fecha_creacion": forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control form-control-sm', 'readonly': 'readonly'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return nombre.title()

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        pais = cleaned_data.get('pais')

        if nombre and pais:
            queryset = Ciudad.objects.filter(nombre__iexact=nombre, pais=pais)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                self.add_error('nombre', 'La Ciudad ya existe para este País.')
        return cleaned_data

class EstadoForm(forms.ModelForm):
    class Meta:
        model = Estado
        fields = ['nombre', 'fecha_creacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nombre del Estado'}),
            "fecha_creacion": forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control form-control-sm', 'readonly': 'readonly'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return nombre.title()
