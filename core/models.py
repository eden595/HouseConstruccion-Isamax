from django.db import models
from django.conf import settings
from django.utils import timezone
from .choices import ESTADO_CHOICES, ESTADO_INACTIVO

class Pais(models.Model):
    """Modelo para almacenar países"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre País")
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=ESTADO_INACTIVO, verbose_name="Estado")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paises_creados", 
        verbose_name="Creado por"
    )
    fecha_creacion = models.DateField(default=timezone.now, verbose_name="Fecha Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Fecha Modificación")
    
    class Meta:

        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return self.nombre
             
class Ciudad(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Ciudad")
    pais = models.ForeignKey(
        Pais, 
        on_delete=models.PROTECT,
        related_name='ciudades',
        verbose_name="País",
        limit_choices_to={'estado': 1}  
    )
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=ESTADO_INACTIVO, verbose_name="Estado")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ciudades_creadas',
        verbose_name="Creado por"
    )
    fecha_creacion = models.DateField(default=timezone.now, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Modificación")

    class Meta:

        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['nombre']
        unique_together = [['nombre', 'pais']]  
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.pais.nombre})"
        
class Estado(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Estado")
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=ESTADO_INACTIVO, verbose_name="Estado")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='estados_creados',
        verbose_name="Creado por"
    )
    fecha_creacion = models.DateField(default=timezone.now, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Modificación")

    class Meta:

        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return self.nombre
