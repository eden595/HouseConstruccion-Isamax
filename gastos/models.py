from django.db import models
from django.contrib.auth import get_user_model
from core.choices import ESTADO_GASTO_CHOICES, ESTADO_GASTO_ACTIVO
from obras.models import Obra

User = get_user_model()

class Proveedor(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    rut = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=30)
    estado = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateField()
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="proveedores_creados")

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

class Categoria(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    estado = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateField()
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="categorias_creadas")

    def __str__(self):
        return self.nombre

class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    estado = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateField()
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tipos_creados")

    def __str__(self):
        return self.nombre

class Gasto(models.Model):
    obra = models.ForeignKey(Obra, on_delete=models.PROTECT, related_name="gastos", verbose_name="Obra")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="gastos")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="gastos")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, related_name="gastos")

    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="gastos_creados")
    fecha_creacion = models.DateField()
    estado = models.BooleanField(default=True, verbose_name="Activo")
    foto = models.ImageField(upload_to="gastos/", null=True, blank=True)
    sin_foto = models.BooleanField(default=False)
    nota = models.TextField(blank=True)

    def __str__(self):
        return f"Gasto {self.id} - {self.obra}"
