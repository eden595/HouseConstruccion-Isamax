from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import ProtectedError, Q
from .models import Pais, Ciudad, Estado
from .forms import PaisForm, CiudadForm, EstadoForm
from core.choices import ESTADO_ACTIVO, ESTADO_INACTIVO

#PAIS
@login_required
def paises_list(request):
    paises = Pais.objects.all().order_by('nombre')
    return render(request, 'core/pais/paises_list.html', {'paises': paises})

@login_required
def pais_create(request):
    if request.method == 'POST':
        form = PaisForm(request.POST)
        if form.is_valid():
            pais = form.save(commit=False)
            pais.creado_por = request.user
            pais.estado = ESTADO_INACTIVO
            pais.save()
            messages.success(request, 'País creado exitosamente.')
            return redirect('core:paises_list')
    else:
        form = PaisForm()
    
    return render(request, 'core/pais/pais_form.html', {'form': form, 'title': 'Crear País'})

@login_required
def pais_update(request, pk):
    pais = get_object_or_404(Pais, pk=pk)
    if request.method == 'POST':
        form = PaisForm(request.POST, instance=pais)
        if form.is_valid():
            pais = form.save(commit=False)
            pais.creado_por = request.user
            pais.save()
            messages.success(request, 'País actualizado exitosamente.')
            return redirect('core:paises_list')
    else:
        form = PaisForm(instance=pais)
    
    return render(request, 'core/pais/pais_form.html', {'form': form, 'title': 'Editar País'})

@login_required
def pais_delete(request, pk):
    pais = get_object_or_404(Pais, pk=pk)
    try:
        pais.delete()
        messages.success(request, 'País eliminado exitosamente.')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar el país porque tiene registros relacionados.')
    
    return redirect('core:paises_list')

@login_required
def pais_toggle_estado(request, pk):
    if request.method == 'POST':
        pais = get_object_or_404(Pais, pk=pk)
        nuevo_estado = ESTADO_INACTIVO if pais.estado == ESTADO_ACTIVO else ESTADO_ACTIVO
        pais.estado = nuevo_estado
        pais.save()
        return JsonResponse({'success': True, 'estado': pais.estado})
    return JsonResponse({'success': False}, status=400)

#CIUDAD
@login_required
def ciudades_list(request):
    ciudades = Ciudad.objects.select_related('pais').all().order_by('nombre')
    return render(request, 'core/ciudad/ciudades_list.html', {'ciudades': ciudades})

@login_required
def ciudad_create(request):
    if request.method == 'POST':
        form = CiudadForm(request.POST)
        if form.is_valid():
            ciudad = form.save(commit=False)
            ciudad.creado_por = request.user
            ciudad.estado = ESTADO_INACTIVO
            ciudad.save()
            messages.success(request, 'Ciudad creada exitosamente.')
            return redirect('core:ciudades_list')
    else:
        form = CiudadForm()
    
    return render(request, 'core/ciudad/ciudad_form.html', {'form': form, 'title': 'Crear Ciudad'})

@login_required
def ciudad_update(request, pk):
    ciudad = get_object_or_404(Ciudad, pk=pk)
    if request.method == 'POST':
        form = CiudadForm(request.POST, instance=ciudad)
        if form.is_valid():
            ciudad = form.save(commit=False)
            ciudad.creado_por = request.user
            ciudad.save()
            messages.success(request, 'Ciudad actualizada exitosamente.')
            return redirect('core:ciudades_list')
    else:
        form = CiudadForm(instance=ciudad)
    
    return render(request, 'core/ciudad/ciudad_form.html', {'form': form, 'title': 'Editar Ciudad'})

@login_required
def ciudad_delete(request, pk):
    ciudad = get_object_or_404(Ciudad, pk=pk)
    try:
        ciudad.delete()
        messages.success(request, 'Ciudad eliminada exitosamente.')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar la ciudad porque tiene registros relacionados.')
    return redirect('core:ciudades_list')

@login_required
def ciudad_toggle_estado(request, pk):
    if request.method == 'POST':
        ciudad = get_object_or_404(Ciudad, pk=pk)
        nuevo_estado = ESTADO_INACTIVO if ciudad.estado == ESTADO_ACTIVO else ESTADO_ACTIVO
        ciudad.estado = nuevo_estado
        ciudad.save()
        return JsonResponse({'success': True, 'estado': ciudad.estado})
    return JsonResponse({'success': False}, status=400)

#ESTADO
@login_required
def estados_list(request):
    estados = Estado.objects.all().order_by('nombre')
    return render(request, 'core/estado/estados_list.html', {'estados': estados})

@login_required
def estado_create(request):
    if request.method == 'POST':
        form = EstadoForm(request.POST)
        if form.is_valid():
            estado = form.save(commit=False)
            estado.creado_por = request.user
            estado.estado = ESTADO_INACTIVO
            estado.save()
            messages.success(request, 'Estado creado exitosamente.')
            return redirect('core:estados_list')
    else:
        form = EstadoForm()
    
    return render(request, 'core/estado/estado_form.html', {'form': form, 'title': 'Crear Estado'})

@login_required
def estado_update(request, pk):
    estado = get_object_or_404(Estado, pk=pk)
    if request.method == 'POST':
        form = EstadoForm(request.POST, instance=estado)
        if form.is_valid():
            if not form.has_changed():
                messages.info(request, 'No se realizaron cambios.')
                return redirect('core:estados_list')
            estado = form.save(commit=False)
            estado.creado_por = request.user
            estado.save()
            messages.success(request, 'Estado actualizado exitosamente.')
            return redirect('core:estados_list')
    else:
        form = EstadoForm(instance=estado)
    
    return render(request, 'core/estado/estado_form.html', {'form': form, 'title': 'Editar Estado'})

@login_required
def estado_delete(request, pk):
    estado = get_object_or_404(Estado, pk=pk)
    try:
        estado.delete()
        messages.success(request, 'Estado eliminado exitosamente.')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar el estado porque está en uso.')
    return redirect('core:estados_list')

@login_required
def estado_toggle_estado(request, pk):
    if request.method == 'POST':
        estado = get_object_or_404(Estado, pk=pk)
        nuevo_estado = ESTADO_INACTIVO if estado.estado == ESTADO_ACTIVO else ESTADO_ACTIVO
        estado.estado = nuevo_estado
        estado.save()
        return JsonResponse({'success': True, 'estado': estado.estado})
    return JsonResponse({'success': False}, status=400)
