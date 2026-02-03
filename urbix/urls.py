from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from administrador import views as admin_views

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/assets/images/favicon.png', permanent=True)),
    # Home / Dashboard
    path('', include('accounts.urls')),
    # Gastos (incluye rendición)
    path('', include('gastos.urls')),
    # Administrador / Usuarios
    path('', include('administrador.urls')),
    # Obra
    path('obras/', include('obras.urls')),
    # Core (Paises, Ciudades, Estados)
    path('', include('core.urls')),
    # Admin Django
    path('admin/', admin.site.urls),
]
# Servir archivos MEDIA en desarrollo (fotos de perfil, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
