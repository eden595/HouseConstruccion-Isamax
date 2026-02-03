from django.urls import path
from gastos import views as gastos_views

urlpatterns = [
    # Proveedores
    path('administrador/gastos/proveedores/', gastos_views.proveedores_lista, name='admin_proveedores'),
    path('administrador/gastos/proveedores/nuevo/', gastos_views.proveedor_crear, name='admin_proveedores_create'),
    path('administrador/gastos/proveedores/<int:pk>/editar/', gastos_views.proveedor_editar, name='admin_proveedores_edit'),
    path('administrador/gastos/proveedores/<int:pk>/toggle/', gastos_views.proveedor_toggle_estado, name='admin_proveedores_toggle'),

    # Categorías
    path('administrador/gastos/categorias/', gastos_views.categorias_lista, name='admin_categorias'),
    path('administrador/gastos/categorias/nueva/', gastos_views.categoria_crear, name='admin_categorias_create'),
    path('administrador/gastos/categorias/<int:pk>/editar/', gastos_views.categoria_editar, name='admin_categorias_edit'),
    path('administrador/gastos/categorias/<int:pk>/toggle/', gastos_views.categoria_toggle_estado, name='admin_categorias_toggle'),

    # Tipos de documento
    path('administrador/gastos/tipo-documento/', gastos_views.tipo_documento_lista, name='admin_tipo_documento'),
    path('administrador/gastos/tipo-documento/nuevo/', gastos_views.tipo_documento_crear, name='admin_tipo_documento_create'),
    path('administrador/gastos/tipo-documento/<int:pk>/editar/', gastos_views.tipo_documento_editar, name='admin_tipo_documento_edit'),
    path('administrador/gastos/tipo-documento/<int:pk>/toggle/', gastos_views.tipo_documento_toggle_estado, name='admin_tipo_documento_toggle'),

    # Rendición de gastos
    path('administrador/gastos/rendicion/', gastos_views.gasto_lista, name='admin_gasto_lista'),
    path('administrador/gastos/rendicion/nuevo/', gastos_views.gasto_crear, name='admin_gasto_ingresar'),
    path('administrador/gastos/rendicion/<int:pk>/editar/', gastos_views.gasto_editar, name='admin_gasto_editar'),
    path('administrador/gastos/rendicion/<int:pk>/toggle/', gastos_views.gasto_toggle_estado, name='admin_gasto_toggle'),
]
