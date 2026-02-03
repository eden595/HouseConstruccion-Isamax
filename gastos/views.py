from datetime import datetime
import json
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from .models import Proveedor, Categoria, TipoDocumento, Gasto
from .forms import ProveedorForm, CategoriaForm, TipoDocumentoForm, GastoForm

# Proveedores
def proveedores_lista(request):
    proveedores = Proveedor.objects.all().order_by("id")
    return render(request, "gastos/proveedores/lista.html", {"proveedores": proveedores})

def proveedor_crear(request):
    if request.method == "POST":
        data = request.POST.copy()
        fecha_str = (data.get("fecha_creacion") or "").strip()
        if fecha_str:
            sep = "-" if "-" in fecha_str else "/" if "/" in fecha_str else None
            if sep:
                parts = fecha_str.split(sep)
                if len(parts) == 3 and len(parts[0]) == 2 and len(parts[2]) == 4:
                    d, m, y = parts
                    data["fecha_creacion"] = f"{y}-{m}-{d}"
        else:
            data["fecha_creacion"] = datetime.now().date().isoformat()

        form = ProveedorForm(data)
        if form.is_valid():
            prov = form.save(commit=False)
            prov.creado_por = request.user if request.user.is_authenticated else None
            prov.estado = False
            try:
                prov.save()
                messages.success(request, "Proveedor creado correctamente.")
                return redirect("admin_proveedores")
            except IntegrityError:
                messages.error(request, "No se pudo guardar el proveedor (posible RUT duplicado).")
    else:
        form = ProveedorForm(initial={"fecha_creacion": datetime.now().date()})
    return render(request, "gastos/proveedores/crear.html", {"form": form})

def proveedor_editar(request, pk=None):
    if pk is None:
        pk = request.GET.get("id")
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == "POST":
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            prov = form.save(commit=False)
            if not prov.creado_por:
                prov.creado_por = request.user if request.user.is_authenticated else None
            prov.creado_por = request.user
            prov.save()
            messages.success(request, "Proveedor actualizado correctamente.")
            return redirect("admin_proveedores")
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, "gastos/proveedores/editar.html", {"form": form, "proveedor": proveedor})

def proveedor_toggle_estado(request, pk=None):
    if pk is None:
        pk = request.GET.get("id")
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == "POST":
        proveedor.estado = False if proveedor.estado else True
        proveedor.save()
    return redirect("admin_proveedores")

# Categorias
def categorias_lista(request):
    categorias = Categoria.objects.all().order_by("id")
    return render(request, "gastos/categorias/lista.html", {"categorias": categorias})

def categoria_crear(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.creado_por = request.user if request.user.is_authenticated else None
            cat.estado = False
            cat.save()
            messages.success(request, "Categoria creada correctamente.")
            return redirect("admin_categorias")

    else:
        form = CategoriaForm(initial={"fecha_creacion": datetime.now().date()})
    return render(request, "gastos/categorias/crear.html", {"form": form})

def categoria_editar(request, pk=None):
    if pk is None:
        pk = request.GET.get("id")
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            cat = form.save(commit=False)
            if not cat.creado_por:
                cat.creado_por = request.user if request.user.is_authenticated else None
            cat.creado_por = request.user
            cat.save()
            messages.success(request, "Categoria actualizada correctamente.")
            return redirect("admin_categorias")

    else:
        form = CategoriaForm(instance=categoria)
    return render(request, "gastos/categorias/editar.html", {"form": form, "categoria": categoria})

def categoria_toggle_estado(request, pk=None):
    if pk is None:
        pk = request.GET.get("id")
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        categoria.estado = False if categoria.estado else True
        categoria.save()
    return redirect("admin_categorias")

# Tipos de documento
def tipo_documento_lista(request):
    docs = TipoDocumento.objects.all().order_by("id")
    return render(request, "gastos/tipo_documento/lista.html", {"docs": docs})

def tipo_documento_crear(request):
    if request.method == "POST":
        form = TipoDocumentoForm(request.POST)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.creado_por = request.user if request.user.is_authenticated else None
            doc.estado = False
            doc.save()
            messages.success(request, "Tipo de documento creado correctamente.")
            return redirect("admin_tipo_documento")

    else:
        form = TipoDocumentoForm(initial={"fecha_creacion": datetime.now().date()})
    return render(request, "gastos/tipo_documento/crear.html", {"form": form})

def tipo_documento_editar(request, pk=None):
    if pk is None:
        pk = request.GET.get("id")
    doc = get_object_or_404(TipoDocumento, pk=pk)
    if request.method == "POST":
        form = TipoDocumentoForm(request.POST, instance=doc)
        if form.is_valid():
            td = form.save(commit=False)
            if not td.creado_por:
                td.creado_por = request.user if request.user.is_authenticated else None
            td.creado_por = request.user
            td.save()
            messages.success(request, "Tipo de documento actualizado correctamente.")
            return redirect("admin_tipo_documento")

    else:
        form = TipoDocumentoForm(instance=doc)
    return render(request, "gastos/tipo_documento/editar.html", {"form": form, "doc": doc})

def tipo_documento_toggle_estado(request, pk=None):
    if pk is None:
        pk = request.GET.get("id")
    doc = get_object_or_404(TipoDocumento, pk=pk)
    if request.method == "POST":
        doc.estado = False if doc.estado else True
        doc.save()
    return redirect("admin_tipo_documento")

# Gastos / Rendicion
def gasto_lista(request):
    gastos = Gasto.objects.select_related("categoria", "proveedor", "tipo_documento", "creado_por").all().order_by("-fecha")
    for gasto in gastos:
        fotos = []
        if getattr(gasto, "foto", None):
            fotos.append({
                "url": gasto.foto.url,
                "name": gasto.foto.name or "",
            })
        gasto.photos_data = fotos
        gasto.photos_data_json = json.dumps(fotos, ensure_ascii=False)
    return render(request, "gastos/rendicion_gastos/lista.html", {"gastos": gastos})

def gasto_crear(request):
    if request.method == "POST":
        form = GastoForm(request.POST, request.FILES)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.fecha = form.cleaned_data.get("fecha") or datetime.now().date()

            gasto.creado_por = request.user if request.user.is_authenticated else None
            gasto.fecha_creacion = form.cleaned_data.get("fecha_creacion") or gasto.fecha
            if gasto.sin_foto:
                gasto.foto = None
            gasto.save()
            messages.success(request, "Gasto creado correctamente.")
            return redirect("admin_gasto_lista")

    else:
        form = GastoForm(initial={"fecha": datetime.now().date(), "fecha_creacion": datetime.now().date(), "estado": True})
    return render(request, "gastos/rendicion_gastos/crear.html", {"form": form})

def gasto_editar(request, pk=None):
    if pk is None:
        pk = request.GET.get("id") or request.GET.get("editar")
    gasto = get_object_or_404(Gasto, pk=pk)
    estado_original = getattr(gasto, "estado", True)
    if request.method == "POST":
        form = GastoForm(request.POST, request.FILES, instance=gasto)
        if form.is_valid():
            ignored = {"estado", "sin_foto", "foto"}
            changed = [field for field in form.changed_data if field not in ignored]
            if not changed and not form.files:
                messages.info(request, "No se realizaron cambios.")
                return redirect("admin_gasto_lista")
            g = form.save(commit=False)
            new_fecha = form.cleaned_data.get("fecha") or g.fecha or datetime.now().date()
            g.fecha = new_fecha

            if g.sin_foto:
                g.foto = None
            g.fecha_creacion = form.cleaned_data.get("fecha_creacion") or g.fecha_creacion or new_fecha
            g.estado = estado_original
            g.save()
            messages.success(request, "Gasto actualizado correctamente.")
            return redirect("admin_gasto_lista")

    else:
        form = GastoForm(
            instance=gasto,
            initial={
                "fecha": gasto.fecha or datetime.now().date(),
                "fecha_creacion": gasto.fecha_creacion or gasto.fecha or datetime.now().date(),
            },
        )
        if not form.initial.get("fecha_creacion") and getattr(gasto, "fecha_creacion", None):
            form.initial["fecha_creacion"] = gasto.fecha_creacion
    return render(request, "gastos/rendicion_gastos/editar.html", {"form": form, "gasto": gasto})

def gasto_toggle_estado(request, pk=None):
    if pk is None:
        pk = request.GET.get("id")
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == "POST":
        gasto.estado = False if getattr(gasto, "estado", True) else True
        gasto.save()
    return redirect("admin_gasto_lista")
