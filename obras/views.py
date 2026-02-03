from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from decimal import Decimal, InvalidOperation
from django.db.models import Q, ProtectedError, Prefetch
from django.utils import timezone
import json
from core.models import Pais, Ciudad, Estado
from obras.models import ( Obra, RegistroLibroObra, TareaRealizada, TrabajadorRegistro, FotografiaRegistro)
from .forms import ObraForm, RegistroLibroObraForm
import datetime
import os
import logging
logger = logging.getLogger(__name__)

MAX_ARCHIVOS_POR_REGISTRO = 20
MAX_FILE_SIZE = 10 * 1024 * 1024
EXTENSIONES_PERMITIDAS = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.mkv', '.webp'}
MAX_HORAS_TOTAL = Decimal("12.0")

# VISTAS OBRA
@login_required
def obra_list(request):
    """Listar obras."""
    try:
        obras = Obra.objects.select_related('ciudad__pais', 'estado_obra', 'creado_por').all()
        context = {
            'obras': obras,
            'title': 'Administración de Obras'
        }
        return render(request, 'obras/obras_list.html', context)
    except Exception as e:
        messages.error(request, f'Error al cargar obras: {str(e)}')
        return render(request, 'obras/obras_list.html', {'obras': [], 'title': 'Administración de Obras'})

@login_required
def obra_create(request):
    """Crear obra."""
    form = ObraForm(request.POST or None)
    ciudades = Ciudad.objects.filter(estado=True).select_related('pais').order_by('nombre')
    estados = Estado.objects.filter(estado=True).order_by('nombre')

    if request.method == 'POST':
        if form.is_valid():
            if Obra.objects.filter(codigo__iexact=form.cleaned_data["codigo"]).exists():
                form.add_error("codigo", f'El código "{form.cleaned_data["codigo"]}" ya existe')
            else:
                obra = form.save(commit=False)
                obra.creado_por = request.user
                obra.save()
                messages.success(request, f'Obra "{obra.nombre}" creada exitosamente.')
                return redirect('obra_list')
        else:
            if 'codigo' not in form.errors:
                messages.error(request, 'Revisa los errores del formulario.')

    if not ciudades.exists():
        messages.warning(request, 'No hay ciudades activas. Debe crear al menos una ciudad antes de crear una obra.')

    if not estados.exists():
        messages.warning(request, 'No hay estados activos. Debe crear al menos un estado antes de crear una obra.')

    context = {
        'form': form,
        'obra': None,
        'ciudades': ciudades,
        'estados': estados,
        'title': 'Crear Obra',
        'no_changes': False,
    }
    return render(request, 'obras/obra_form.html', context)

@login_required
def obra_update(request, pk):
    """Actualizar obra."""
    obra = get_object_or_404(Obra, pk=pk)
    form = ObraForm(request.POST or None, instance=obra)
    original_estado = obra.estado
    ciudades = Ciudad.objects.filter(estado=True).select_related('pais').order_by('nombre')
    estados = Estado.objects.filter(estado=True).order_by('nombre')
    context = {
        'obra': obra,
        'form': form,
        'ciudades': ciudades,
        'estados': estados,
        'title': 'Editar Obra',
        'no_changes': False,
    }

    if request.method == 'POST':
        if not form.has_changed():
            form = ObraForm(instance=obra)
            context['form'] = form
            context['no_changes'] = True
            messages.info(request, 'No se realizaron cambios.')
        elif form.is_valid():
            if Obra.objects.filter(codigo__iexact=form.cleaned_data["codigo"]).exclude(pk=pk).exists():
                form.add_error("codigo", f'El código "{form.cleaned_data["codigo"]}" ya existe')
            else:
                obra_obj = form.save(commit=False)
                # Evita que el estado activo/inactivo cambie al guardar
                obra_obj.estado = original_estado
                obra_obj.creado_por = request.user
                obra_obj.save()
                form.save_m2m()
                messages.success(request, 'Ha sido actualizado con éxito.')
                return redirect('obra_list')
        else:
            if 'codigo' not in form.errors:
                messages.error(request, 'Revisa los errores del formulario.')

    if not ciudades.exists():
        messages.warning(request, 'No hay ciudades activas disponibles.')

    if not estados.exists():
        messages.warning(request, 'No hay estados activos disponibles.')

    try:
        return render(request, 'obras/obra_form.html', context)
    except Exception as e:
        messages.error(request, f'Error al cargar el formulario: {str(e)}')
        return redirect('obra_list')

@login_required
@require_POST
def obra_delete(request, pk):
    """Eliminar obra."""
    obra = get_object_or_404(Obra, pk=pk)
    nombre = obra.nombre
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    try:
        if obra.registros.exists():
            count = obra.registros.count()
            msg = f'No se puede eliminar la obra "{nombre}" porque tiene {count} registro(s) de libro de obras asociado(s).'
            if is_ajax:
                return JsonResponse({'success': False, 'message': msg}, status=400)
            messages.error(request, msg)
            return redirect('obra_list')
        
        obra.delete()
        msg = f'Obra "{nombre}" eliminada correctamente.'
        if is_ajax:
            return JsonResponse({'success': True, 'message': msg})
        messages.success(request, msg)
    except ProtectedError:
        msg = f'No se puede eliminar la obra "{nombre}" porque tiene registros relacionados protegidos.'
        if is_ajax:
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
    except Exception as e:
        msg = f'Error al eliminar obra: {str(e)}'
        if is_ajax:
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
    
    return redirect('obra_list')

@login_required
def obra_toggle_estado(request, pk):
    """Activar/Desactivar obra via AJAX."""
    if request.method == 'POST':
        try:
            obra = get_object_or_404(Obra, pk=pk)
            
            if obra.estado and obra.registros.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'No se puede desactivar porque tiene registros de libro de obras asociados.'
                })
            
            obra.estado = not obra.estado
            obra.save()
            
            return JsonResponse({
                'success': True,
                'estado': obra.estado,
                'message': 'Ha sido actualizado con éxito.'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

# VISTAS LIBRO DE OBRAS
@login_required
def registro_libro_list(request):
    """Listar registros del libro de obras."""
    registros = list(
        RegistroLibroObra.objects
        .select_related('obra', 'supervisor')
        .prefetch_related(
            'tareas',
            'trabajadores__trabajador',
            Prefetch('fotografias', queryset=FotografiaRegistro.objects.order_by('orden'))
        )
        .all()
    )

    for registro in registros:
        fotos = []

        # Incluimos la foto principal (campo fotografia) si existe
        if getattr(registro, "fotografia", None):
            try:
                fotos.append({
                    "url": registro.fotografia.url,
                    "name": registro.fotografia.name or "",
                })
            except Exception:
                pass

        # Incluimos todas las fotografías/vídeos asociados (ordenadas)
        for foto in registro.fotografias.all():
            if not foto.archivo:
                continue
            try:
                fotos.append({
                    "url": foto.archivo.url,
                    "name": foto.archivo.name or "",
                })
            except Exception:
                continue

        registro.photos_data = fotos
        registro.photos_data_json = json.dumps(fotos, ensure_ascii=False)

    context = {
        'registros': registros,
        'title': 'Registros Libro de Obras'
    }
    return render(request, 'obras/registro_libro_list.html', context)

@login_required
def registro_libro_create(request):
    """Crear registro del libro de obras."""
    if request.method == 'POST':
        try:
            obra_id = request.POST.get('obra')
            fecha = request.POST.get('fecha')
            observaciones = request.POST.get('observaciones', '')
            
            registro = RegistroLibroObra.objects.create(
                obra_id=obra_id,
                fecha=fecha,
                supervisor=request.user,
                observaciones=observaciones,
                creado_por=request.user
            )
            
            if 'fotografia' in request.FILES:
                registro.fotografia = request.FILES['fotografia']
                registro.save()
            
            archivos = request.FILES.getlist('archivos[]')
            for i, archivo in enumerate(archivos):
                tipo = 'video' if archivo.content_type.startswith('video/') else 'imagen'
                FotografiaRegistro.objects.create(
                    registro=registro,
                    archivo=archivo,
                    tipo=tipo,
                    orden=i
                )
            
            tareas = request.POST.getlist('tarea[]')
            for i, tarea_desc in enumerate(tareas):
                if tarea_desc.strip():
                    TareaRealizada.objects.create(
                        registro=registro,
                        descripcion=tarea_desc,
                        orden=i+1
                    )
            
            trabajadores = request.POST.getlist('trabajador[]')
            horas = request.POST.getlist('horas[]')
            horas_extras = request.POST.getlist('horas_extra[]')

            # Validar duplicados
            trabajadores_limpios = [t for t in trabajadores if t]
            if len(trabajadores_limpios) != len(set(trabajadores_limpios)):
                raise ValidationError("Un trabajador no puede repetirse en el mismo registro.")
            if str(request.user.id) in trabajadores_limpios:
                raise ValidationError("El supervisor no puede ser seleccionado como trabajador.")

            def normaliza_par(h_str, extra_str, min_base=Decimal("0")):
                def to_decimal(val):
                    try:
                        return Decimal(str(val).replace(',', '.'))
                    except Exception:
                        return Decimal("0")

                base = to_decimal(h_str)
                extra = to_decimal(extra_str)
                if base < 0:
                    base = Decimal("0")
                if extra < 0:
                    extra = Decimal("0")

                total = base + extra
                if total > MAX_HORAS_TOTAL:
                    raise ValidationError("La suma de horas y horas extra no puede superar 12 por trabajador.")
                if base > MAX_HORAS_TOTAL:
                    raise ValidationError("Las horas normales no pueden superar 12 por trabajador.")
                if min_base > 0 and base < min_base:
                    raise ValidationError("Las horas normales deben ser al menos 1 por trabajador.")
                return (base.quantize(Decimal("0.01")), extra.quantize(Decimal("0.01")))

            for trabajador_id, horas_val, extra_val in zip(trabajadores, horas, horas_extras):
                if trabajador_id and (horas_val or extra_val):
                    h_norm, extra_norm = normaliza_par(horas_val, extra_val, min_base=Decimal("1"))
                    TrabajadorRegistro.objects.create(
                        registro=registro,
                        trabajador_id=trabajador_id,
                        horas_trabajadas=h_norm,
                        horas_extras=extra_norm
                    )
            
            messages.success(request, 'Registro guardado exitosamente')
            return redirect('registro_libro_list')
            
        except Exception as e:
            messages.error(request, f'Error al guardar: {str(e)}')
    
    obras = Obra.objects.filter(estado=True)
    trabajadores = User.objects.exclude(id=request.user.id).filter(is_active=True)
    today = datetime.date.today()
    
    return render(request, 'obras/registro_libro_form.html', {
        'title': 'Ingresar Registro',
        'obras': obras,
        'trabajadores': trabajadores,
        'registro': None,
        'registro_trabajadores': [],
        'today': today
    })

@login_required
def registro_libro_update(request, pk):
    """Actualizar registro del libro de obras."""
    registro = get_object_or_404(RegistroLibroObra, pk=pk)
    originales = {
        "obra": str(registro.obra_id),
        "fecha": registro.fecha.isoformat() if registro.fecha else "",
        "observaciones": registro.observaciones or "",
        "tareas": list(registro.tareas.values_list("descripcion", flat=True)),
        "trabajadores": list(
            registro.trabajadores.values_list("trabajador_id", "horas_trabajadas", "horas_extras")
        ),
    }
    
    if request.method == 'POST':
        try:
            registro.obra_id = request.POST.get('obra')
            new_fecha_str = request.POST.get('fecha') or ''
            new_fecha = None
            if new_fecha_str:
                try:
                    new_fecha = datetime.date.fromisoformat(new_fecha_str)
                except ValueError:
                    new_fecha = registro.fecha
            registro.fecha = new_fecha
            registro.observaciones = request.POST.get('observaciones', '')

            nuevos_archivos = request.FILES.getlist('archivos[]')
            nueva_foto = request.FILES.get('fotografia')
            deleted_ids = request.POST.get('deleted_ids', '')

            tareas = [t.strip() for t in request.POST.getlist('tarea[]') if t.strip()]
            trabajadores = request.POST.getlist('trabajador[]')
            horas = request.POST.getlist('horas[]')
            horas_extras = request.POST.getlist('horas_extra[]')
            trabajadores_data = []

            trabajadores_limpios = [t for t in trabajadores if t]
            if len(trabajadores_limpios) != len(set(trabajadores_limpios)):
                raise ValidationError("Un trabajador no puede repetirse en el mismo registro.")
            if str(request.user.id) in trabajadores_limpios:
                raise ValidationError("El supervisor no puede ser seleccionado como trabajador.")

            def normaliza_par(h_str, extra_str, min_base=Decimal("0")):
                def to_decimal(val):
                    try:
                        return Decimal(str(val).replace(',', '.'))
                    except Exception:
                        return Decimal("0")

                base = to_decimal(h_str)
                extra = to_decimal(extra_str)
                if base < 0:
                    base = Decimal("0")
                if extra < 0:
                    extra = Decimal("0")

                total = base + extra
                if total > MAX_HORAS_TOTAL:
                    raise ValidationError("La suma de horas y horas extra no puede superar 12 por trabajador.")
                if base > MAX_HORAS_TOTAL:
                    raise ValidationError("Las horas normales no pueden superar 12 por trabajador.")
                if min_base > 0 and base < min_base:
                    raise ValidationError("Las horas normales deben ser al menos 1 por trabajador.")
                return (base.quantize(Decimal("0.01")), extra.quantize(Decimal("0.01")))

            for trabajador_id, horas_val, extra_val in zip(trabajadores, horas, horas_extras):
                if trabajador_id and (horas_val or extra_val):
                    base, extra = normaliza_par(horas_val, extra_val, min_base=Decimal("1"))
                    trabajadores_data.append((trabajador_id, base, extra))

            def normalize_trab_list(raw_data):
                norm = []
                for tid, horas_raw, extra_raw in raw_data:
                    try:
                        horas_float = float(horas_raw)
                    except Exception:
                        horas_float = 0.0
                    try:
                        extra_float = float(extra_raw)
                    except Exception:
                        extra_float = 0.0
                    norm.append((str(tid), round(horas_float, 3), round(extra_float, 3)))
                norm.sort(key=lambda x: x[0])
                return norm

            originales_trabajadores = normalize_trab_list(originales["trabajadores"])
            nuevos_trabajadores = normalize_trab_list(trabajadores_data)

            sin_cambios = (
                originales["obra"] == str(registro.obra_id or "")
                and originales["fecha"] == (new_fecha.isoformat() if new_fecha else "")
                and originales["observaciones"] == (registro.observaciones or "")
                and originales["tareas"] == tareas
                and originales_trabajadores == nuevos_trabajadores
                and not nuevos_archivos
                and not nueva_foto
                and not deleted_ids
            )

            if sin_cambios:
                messages.info(request, 'No se realizaron cambios.')
                return redirect('registro_libro_list')

            if nueva_foto:
                registro.fotografia = nueva_foto
            registro.save()

            # Procesar eliminaciones diferidas
            deleted_ids = request.POST.get('deleted_ids', '')
            if deleted_ids:
                ids_to_delete = [int(x) for x in deleted_ids.split(',') if x.strip().isdigit()]
                if ids_to_delete:
                    FotografiaRegistro.objects.filter(id__in=ids_to_delete, registro=registro).delete()

            orden_inicial = registro.fotografias.count()
            for i, archivo in enumerate(nuevos_archivos):
                tipo = 'video' if archivo.content_type.startswith('video/') else 'imagen'
                FotografiaRegistro.objects.create(
                    registro=registro,
                    archivo=archivo,
                    tipo=tipo,
                    orden=orden_inicial + i
                )

            registro.tareas.all().delete()
            for i, tarea_desc in enumerate(tareas):
                TareaRealizada.objects.create(
                    registro=registro,
                    descripcion=tarea_desc,
                    orden=i+1
                )

            registro.trabajadores.all().delete()
            for trabajador_id, horas_num, extra_num in trabajadores_data:
                TrabajadorRegistro.objects.create(
                    registro=registro,
                    trabajador_id=trabajador_id,
                    horas_trabajadas=horas_num,
                    horas_extras=extra_num
                )

            messages.success(request, 'Registro actualizado correctamente.')
            return redirect('registro_libro_list')

        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    
    obras = Obra.objects.filter(estado=True)
    trabajadores = User.objects.exclude(id=request.user.id).filter(is_active=True)
    today = datetime.date.today()
    registro_trabajadores = registro.trabajadores.select_related('trabajador').all()
    
    return render(request, 'obras/registro_libro_form.html', {
        'title': 'Editar Registro',
        'obras': obras,
        'trabajadores': trabajadores,
        'registro': registro,
        'registro_trabajadores': registro_trabajadores,
        'today': today
    })

@login_required
def fotografia_delete(request, pk):
    """Eliminar fotografía del registro."""
    fotografia = get_object_or_404(FotografiaRegistro, pk=pk)
    registro_id = fotografia.registro.id
    fotografia.delete()
    messages.success(request, 'Archivo eliminado exitosamente')
    return redirect('registro_libro_update', pk=registro_id)

@login_required
def registro_libro_delete(request, pk):
    """Eliminar registro del libro de obras."""
    registro = get_object_or_404(RegistroLibroObra, pk=pk)
    
    try:
        registro.delete()
        messages.success(request, 'Registro eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar registro: {str(e)}')
    
    return redirect('registro_libro_list')
