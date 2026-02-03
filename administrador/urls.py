from django.urls import path
from . import views as admin_views

urlpatterns = [
    path('administrador/usuario/', admin_views.usuarios_lista, name='admin_users'),
    path('administrador/usuario/nuevo/', admin_views.usuario_crear, name='admin_users_create'),
    path('administrador/usuario/<int:pk>/editar/', admin_views.usuario_editar, name='admin_users_edit'),
    path('administrador/usuario/<int:pk>/eliminar/', admin_views.usuario_eliminar, name='admin_users_delete'),
    path('administrador/usuario/<int:pk>/toggle/', admin_views.usuario_toggle_estado, name='admin_users_toggle'),
]
