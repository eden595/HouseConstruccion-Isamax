from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.db import IntegrityError, connection
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

User = get_user_model()


# ---------------- Usuarios ----------------
def usuarios_lista(request):
    query = request.GET.get("q", "").strip()
    usuarios = User.objects.all().prefetch_related("groups")
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(groups__name__icontains=query)
        ).distinct()
    usuarios = usuarios.order_by("id")
    return render(request, "administrador/usuario/lista.html", {"usuarios": usuarios, "q": query})


def usuario_crear(request):
    grupos = Group.objects.all()
    context = {"grupos": grupos}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        group_id = request.POST.get("group_id")
        errors = []
        if not username or not email or not password or not password2 or not group_id:
            errors.append("Todos los campos son obligatorios.")
        if password != password2:
            errors.append("Las contraseñas no coinciden.")
        if username and User.objects.filter(username=username).exists():
            errors.append("Ya existe un usuario con ese nombre.")
        if email and User.objects.filter(email=email).exists():
            errors.append("Ya existe un usuario con ese correo.")

        context.update(
            {
                "username_val": username,
                "email_val": email,
                "group_selected": group_id,
                "errors": errors,
            }
        )

        if not errors:
            try:
                validate_password(password, user=User(username=username, email=email))
            except ValidationError as exc:
                errors.extend(exc.messages)

        if not errors:
            user = User.objects.create_user(username=username, email=email, password=password)
            group = Group.objects.filter(id=group_id).first()
            if group:
                user.groups.add(group)
            messages.success(request, "Usuario creado correctamente.")
            return redirect("admin_users")
    return render(request, "administrador/usuario/crear.html", context)


def usuario_editar(request, pk=None):
    if pk is None:
        return redirect("admin_users")
    usuario = get_object_or_404(User, pk=pk)
    grupos = Group.objects.all()
    context = {
        "usuario": usuario,
        "grupos": grupos,
        "grupo_actual": usuario.groups.first(),
        "no_changes": False,
    }
    group_id = None
    if request.method == "POST":
        original = {
            "username": usuario.username,
            "email": usuario.email,
            "first_name": usuario.first_name,
            "last_name": usuario.last_name,
            "group_ids": list(usuario.groups.values_list("id", flat=True)),
            "fecha_creacion": usuario.date_joined,
        }

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        group_id = request.POST.get("group_id")
        fecha_creacion_str = request.POST.get("fecha_creacion", "").strip()

        errors = []
        if not username or not email or not group_id:
            errors.append("Usuario, correo y rol son obligatorios.")
        if username and User.objects.exclude(id=usuario.id).filter(username=username).exists():
            errors.append("Ya existe otro usuario con ese nombre.")
        if email and User.objects.exclude(id=usuario.id).filter(email=email).exists():
            errors.append("Ya existe otro usuario con ese correo.")

        if errors:
            for err in errors:
                messages.warning(request, err)
        else:
            usuario.username = username or usuario.username
            usuario.email = email or usuario.email
            usuario.first_name = first_name
            usuario.last_name = last_name
            if fecha_creacion_str:
                try:
                    dt = datetime.strptime(fecha_creacion_str, "%Y-%m-%d")
                    if settings.USE_TZ:
                        dt = timezone.make_aware(dt, timezone.get_current_timezone())
                    usuario.date_joined = dt
                except ValueError:
                    messages.warning(request, "Fecha de creación inválida, se mantiene la anterior.")

            try:
                usuario.groups.clear()
                if group_id:
                    group = Group.objects.filter(id=group_id).first()
                    if group:
                        usuario.groups.add(group)

                new_group_ids = list(usuario.groups.values_list("id", flat=True))
                changed = (
                    username != original["username"]
                    or email != original["email"]
                    or first_name != original["first_name"]
                    or last_name != original["last_name"]
                    or set(new_group_ids) != set(original["group_ids"])
                    or usuario.date_joined != original["fecha_creacion"]
                )

                if not changed:
                    context["no_changes"] = True
                    context["grupo_actual"] = Group.objects.filter(id=group_id).first() or usuario.groups.first()
                    return render(request, "administrador/usuario/editar.html", context)

                usuario.save()
                messages.success(request, "Ha sido actualizado con éxito.")
                return redirect("admin_users")
            except IntegrityError:
                messages.error(request, "No se pudo actualizar el usuario (conflicto de datos).")
    context["grupo_actual"] = Group.objects.filter(id=group_id).first() or usuario.groups.first()
    return render(request, "administrador/usuario/editar.html", context)

def usuario_toggle_estado(request, pk=None):
    if pk is None:
        return redirect("admin_users")
    usuario = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        usuario.is_active = not usuario.is_active
        usuario.save()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return render(
                request,
                "administrador/usuario/estado_fragment.html",
                {"usuario": usuario},
            )
    return redirect("admin_users")


def usuario_eliminar(request, pk=None):
    if pk is None:
        return redirect("admin_users")
    usuario = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        try:
            usuario.delete()
        except IntegrityError:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM userprofile_userprofile WHERE user_id = %s", [usuario.id])
            usuario.delete()
        return redirect("admin_users")
    return render(request, "administrador/usuario/eliminar.html", {"usuario": usuario})
