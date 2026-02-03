from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    #PAISES
    path('paises/', views.paises_list, name='paises_list'),
    path('paises/crear/', views.pais_create, name='pais_create'), 
    path('paises/<int:pk>/editar/', views.pais_update, name='pais_update'), 
    path('paises/<int:pk>/eliminar/', views.pais_delete, name='pais_delete'),
    path('paises/<int:pk>/toggle-estado/', views.pais_toggle_estado, name='pais_toggle_estado'),
    #CIUDADES
    path('ciudades/', views.ciudades_list, name='ciudades_list'),
    path('ciudades/crear/', views.ciudad_create, name='ciudad_create'),
    path('ciudades/<int:pk>/editar/', views.ciudad_update, name='ciudad_update'),
    path('ciudades/<int:pk>/eliminar/', views.ciudad_delete, name='ciudad_delete'),
    path('ciudades/<int:pk>/toggle-estado/', views.ciudad_toggle_estado, name='ciudad_toggle_estado'),
    #ESTADOS
    path('estados/', views.estados_list, name='estados_list'),
    path('estados/crear/', views.estado_create, name='estado_create'),
    path('estados/<int:pk>/editar/', views.estado_update, name='estado_update'),
    path('estados/<int:pk>/eliminar/', views.estado_delete, name='estado_delete'),
    path('estados/<int:pk>/toggle-estado/', views.estado_toggle_estado, name='estado_toggle_estado'),
]
