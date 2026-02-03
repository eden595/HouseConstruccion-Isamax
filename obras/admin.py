from django.contrib import admin

from .models import FotografiaRegistro, Obra, RegistroLibroObra, TareaRealizada, TrabajadorRegistro


admin.site.register(Obra)
admin.site.register(RegistroLibroObra)
admin.site.register(FotografiaRegistro)
admin.site.register(TareaRealizada)
admin.site.register(TrabajadorRegistro)
