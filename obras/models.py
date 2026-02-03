from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models import Ciudad, Estado
from core.choices import TIPO_ARCHIVO_CHOICES, TIPO_ARCHIVO_IMAGEN

class Obra(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Obra")
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    direccion = models.CharField(max_length=300, verbose_name="Dirección")
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.PROTECT,
        related_name="obras",
        verbose_name="Ciudad",
        limit_choices_to={"estado": True},
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin_estimada = models.DateField(verbose_name="Fecha Fin Estimada")
    estado_obra = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        related_name="obras",
        verbose_name="Estado",
        limit_choices_to={"estado": True},
    )
    estado = models.BooleanField(default=True, verbose_name="Activo")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="obras_creadas",
        verbose_name="Creado por",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Modificación")

    class Meta:
        db_table = "obras_lista"
        verbose_name = "Obra"
        verbose_name_plural = "Obras"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["estado"]),
        ]

    def clean(self):
        errors = {}
        if self.fecha_inicio and self.fecha_fin_estimada and self.fecha_fin_estimada <= self.fecha_inicio:
            errors["fecha_fin_estimada"] = "La fecha de fin debe ser posterior a la fecha de inicio."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.codigo:
            self.codigo = self.codigo.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class RegistroLibroObra(models.Model):
    obra = models.ForeignKey(
        Obra,
        on_delete=models.PROTECT,
        related_name="registros",
        verbose_name="Obra",
        limit_choices_to={"estado": True},
    )
    fecha = models.DateField(verbose_name="Fecha")
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="registros_supervisados",
        verbose_name="Supervisor",
    )
    observaciones = models.TextField(blank=True, null=True, max_length=1000, verbose_name="Observaciones")
    fotografia = models.ImageField(upload_to="libro_obras/", blank=True, null=True, verbose_name="Fotografía/Video")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="registros_creados",
        verbose_name="Creado por",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Modificación")

    class Meta:
        db_table = "libro_obras_registro"
        verbose_name = "Registro Libro de Obra"
        verbose_name_plural = "Registros Libro de Obra"
        ordering = ["-fecha", "-fecha_creacion"]
        indexes = [
            models.Index(fields=["fecha"]),
            models.Index(fields=["obra", "fecha"]),
        ]

    def __str__(self):
        return f"Registro {self.obra.codigo} - {self.fecha}"

class FotografiaRegistro(models.Model):
    registro = models.ForeignKey(RegistroLibroObra, on_delete=models.CASCADE, related_name="fotografias")
    archivo = models.FileField(upload_to="libro_obras/", verbose_name="Archivo")
    tipo = models.CharField(max_length=10, choices=TIPO_ARCHIVO_CHOICES, default=TIPO_ARCHIVO_IMAGEN)
    orden = models.PositiveIntegerField(default=0)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "libro_obras_foto"
        ordering = ["orden", "fecha_subida"]
        verbose_name = "Fotografía/Video"
        verbose_name_plural = "Fotografías/Videos"
        indexes = [
            models.Index(fields=["registro", "orden"]),
        ]

    def __str__(self):
        return f"{self.registro.obra.nombre} - {self.archivo.name}"

class TareaRealizada(models.Model):
    registro = models.ForeignKey(
        RegistroLibroObra,
        on_delete=models.CASCADE,
        related_name="tareas",
        verbose_name="Registro",
    )
    descripcion = models.CharField(max_length=300, verbose_name="Descripción de la Tarea")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")

    class Meta:
        db_table = "libro_obras_tarea"
        verbose_name = "Tarea Realizada"
        verbose_name_plural = "Tareas Realizadas"
        ordering = ["orden"]

    def __str__(self):
        return self.descripcion

class TrabajadorRegistro(models.Model):
    registro = models.ForeignKey(
        RegistroLibroObra,
        on_delete=models.CASCADE,
        related_name="trabajadores",
        verbose_name="Registro",
    )
    trabajador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="registros_trabajados",
        verbose_name="Trabajador",
        limit_choices_to={"is_active": True},
    )
    horas_trabajadas = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Horas Trabajadas")
    horas_extras = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Horas Extras")

    class Meta:
        db_table = "libro_obras_trabajador"
        verbose_name = "Trabajador en Registro"
        verbose_name_plural = "Trabajadores en Registro"
        ordering = ["id"]

    def __str__(self):
        return f"{self.trabajador.get_full_name()} - {self.horas_trabajadas}h"
