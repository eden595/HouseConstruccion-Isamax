from django import forms
from .models import Obra, RegistroLibroObra, TareaRealizada, TrabajadorRegistro
from core.models import Ciudad, Estado

class ObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = [
            "nombre",
            "codigo",
            "descripcion",
            "direccion",
            "ciudad",
            "fecha_inicio",
            "fecha_fin_estimada",
            "estado_obra",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin_estimada": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ciudad"].queryset = Ciudad.objects.filter(estado=True)
        self.fields["estado_obra"].queryset = Estado.objects.filter(estado=True)

class RegistroLibroObraForm(forms.ModelForm):
    class Meta:
        model = RegistroLibroObra
        fields = [
            "obra",
            "fecha",
            "supervisor",
            "observaciones",
            "fotografia",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["obra"].queryset = Obra.objects.filter(estado=True)

class TareaRealizadaForm(forms.ModelForm):
    class Meta:
        model = TareaRealizada
        fields = ["registro", "descripcion", "orden"]

class TrabajadorRegistroForm(forms.ModelForm):
    class Meta:
        model = TrabajadorRegistro
        fields = ["registro", "trabajador", "horas_trabajadas"]
