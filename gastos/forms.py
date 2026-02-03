from django import forms
import datetime
from .models import Proveedor, Categoria, TipoDocumento, Gasto
from obras.models import Obra
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "rut", "direccion", "telefono", "fecha_creacion"]
        widgets = {
            "fecha_creacion": forms.DateInput(attrs={"type": "date", "readonly": "readonly"}, format="%Y-%m-%d"),
            "nombre": forms.TextInput(attrs={"placeholder": "Nombre del proveedor"}),
            "rut": forms.TextInput(attrs={"placeholder": "12.345.678-9"}),
            "direccion": forms.TextInput(attrs={"placeholder": "Dirección del proveedor"}),
            "telefono": forms.TextInput(attrs={"placeholder": "+56 9 1234 5678"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "fecha_creacion" in self.fields:
            self.fields["fecha_creacion"].input_formats = ["%Y-%m-%d", "%d-%m-%Y"]
            if not self.initial.get("fecha_creacion"):
                self.initial["fecha_creacion"] = datetime.date.today()
        for name, field in self.fields.items():
            css = "form-control form-control-sm"
            if isinstance(field.widget, forms.Select):
                css = "form-select form-select-sm"
            field.widget.attrs.setdefault("class", css)

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "fecha_creacion"]
        widgets = {
            "fecha_creacion": forms.DateInput(attrs={"type": "date", "readonly": "readonly"}, format="%Y-%m-%d"),
            "nombre": forms.TextInput(attrs={"placeholder": "Nombre de la categoría"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "fecha_creacion" in self.fields:
            self.fields["fecha_creacion"].input_formats = ["%Y-%m-%d", "%d-%m-%Y"]
            if not self.initial.get("fecha_creacion"):
                self.initial["fecha_creacion"] = datetime.date.today()
        for name, field in self.fields.items():
            css = "form-control form-control-sm"
            if isinstance(field.widget, forms.Select):
                css = "form-select form-select-sm"
            field.widget.attrs.setdefault("class", css)

class TipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = ["nombre", "fecha_creacion"]
        widgets = {
            "fecha_creacion": forms.DateInput(attrs={"type": "date", "readonly": "readonly"}, format="%Y-%m-%d"),
            "nombre": forms.TextInput(attrs={"placeholder": "Ej: Factura"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "fecha_creacion" in self.fields:
            self.fields["fecha_creacion"].input_formats = ["%Y-%m-%d", "%d-%m-%Y"]
            if not self.initial.get("fecha_creacion"):
                self.initial["fecha_creacion"] = datetime.date.today()
        for name, field in self.fields.items():
            css = "form-control form-control-sm"
            if isinstance(field.widget, forms.Select):
                css = "form-select form-select-sm"
            field.widget.attrs.setdefault("class", css)

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = [
            "obra",
            "categoria",
            "proveedor",
            "monto",
            "fecha",
            "fecha_creacion",
            "tipo_documento",
            "foto",
            "sin_foto",
            "estado",
            "nota",
        ]
        widgets = {
            "fecha": forms.HiddenInput(),
            "fecha_creacion": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "monto": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "estado": forms.HiddenInput(),
            "nota": forms.Textarea(attrs={"rows": 2}),
            "foto": forms.FileInput(attrs={"id": "foto", "accept": "image/*"}),
            "sin_foto": forms.CheckboxInput(attrs={"id": "sin_foto", "class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Permitir fechas en ambos formatos
        if "fecha" in self.fields:
            self.fields["fecha"].input_formats = ["%Y-%m-%d", "%d-%m-%Y"]
            self.fields["fecha"].required = False
            if not self.initial.get("fecha"):
                self.initial["fecha"] = getattr(self.instance, "fecha", None) or datetime.date.today()
        if "fecha_creacion" in self.fields:
            self.fields["fecha_creacion"].input_formats = ["%Y-%m-%d", "%d-%m-%Y"]

        if not getattr(self, "instance", None) or not self.instance.pk:
            self.initial.setdefault("estado", True)

        # Obra como ModelChoiceField para manejar correctamente la ForeignKey
        self.fields["obra"] = forms.ModelChoiceField(
            queryset=Obra.objects.all().order_by("nombre"),
            empty_label="Selecciona una obra",
            required=True,
            label="Obra",
            widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
        )

        # Etiquetas vac?as m?s claras
        if hasattr(self.fields.get("categoria"), "empty_label"):
            self.fields["categoria"].empty_label = "Sin categoría"
        if hasattr(self.fields.get("proveedor"), "empty_label"):
            self.fields["proveedor"].empty_label = "Sin proveedor"
        if hasattr(self.fields.get("tipo_documento"), "empty_label"):
            self.fields["tipo_documento"].empty_label = "Sin tipo de documento"

        if getattr(self, "instance", None) and getattr(self.instance, "pk", None):
            if not self.initial.get("fecha_creacion"):
                fc = getattr(self.instance, "fecha_creacion", None) or getattr(self.instance, "fecha", None)
                if fc:
                    self.initial["fecha_creacion"] = fc
            if not self.initial.get("fecha"):
                self.initial["fecha"] = getattr(self.instance, "fecha", None) or datetime.date.today()
            if "sin_foto" in self.fields:
                self.fields["sin_foto"].initial = getattr(self.instance, "sin_foto", False)

        # CSS por tipo de control
        for name, field in self.fields.items():
            css = "form-control form-control-sm"
            if isinstance(field.widget, forms.Select):
                css = "form-select form-select-sm"
            if name in ["categoria", "proveedor", "tipo_documento"]:
                css = "form-select form-select-sm"
            if name == "sin_foto":
                css = "form-check-input"
            field.widget.attrs.setdefault("class", css)

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is None:
            raise forms.ValidationError("El monto es obligatorio.")
        if monto <= 0:
            raise forms.ValidationError("No se pueden ingresar montos iguales o menores a 0.")
        return monto
