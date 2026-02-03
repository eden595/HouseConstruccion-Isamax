from django.urls import path
from . import views

urlpatterns = [
    # Obras
    path('obras/', views.obra_list, name='obra_list'),
    path('obras/crear/', views.obra_create, name='obra_create'),
    path('obras/editar/<int:pk>/', views.obra_update, name='obra_update'),
    path('obras/eliminar/<int:pk>/', views.obra_delete, name='obra_delete'),
    path('obras/toggle/<int:pk>/', views.obra_toggle_estado, name='obra_toggle_estado'),

    # Libro de Obras
    path('libro-obras/', views.registro_libro_list, name='registro_libro_list'),
    path('libro-obras/crear/', views.registro_libro_create, name='registro_libro_create'),
    path('libro-obras/editar/<int:pk>/', views.registro_libro_update, name='registro_libro_update'),
    path('libro-obras/eliminar/<int:pk>/', views.registro_libro_delete, name='registro_libro_delete'),
    path('libro-obras/fotografia/eliminar/<int:pk>/', views.fotografia_delete, name='fotografia_delete'),
]
