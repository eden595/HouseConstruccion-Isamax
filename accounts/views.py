from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.template import TemplateDoesNotExist
from django.http import JsonResponse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q, ProtectedError
from django.utils import timezone
from accounts.models import Profile
import datetime

def _ensure_roles_exist():
    """Crea los roles basicos si aún no existen."""
    for role_name in ["Administrador", "Supervisor", "Trabajador"]:
        Group.objects.get_or_create(name=role_name)

# HOME / DASHBOARD
@login_required(login_url='signin')
def home_view(request):
    """Vista principal dashboard."""
    return render(request, 'dashboard/index.html')

# AUTENTICACIÓN
def signin_view(request):
    """Vista de inicio de sesión."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = (request.POST.get('username') or "").strip()
        password = (request.POST.get('password') or "").strip()
        remember_me = request.POST.get('rememberMe')

        if not username or not password:
            messages.error(request, "Ingresa tu usuario y contraseña.")
            return render(request, 'accounts/auth/iniciar_sesion.html')


        try_user = User.objects.filter(username=username).first()

        if try_user is None:
            messages.error(request, "Este usuario no existe.")
            return render(request, 'accounts/auth/iniciar_sesion.html')

        if not try_user.is_active:
            messages.warning(request, "Tu cuenta aún no está habilitada por un administrador.")
            return render(request, 'accounts/auth/iniciar_sesion.html')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, 'accounts/auth/iniciar_sesion.html')

        login(request, user)

        if not remember_me:
            request.session.set_expiry(0)

        return redirect('home')

    return render(request, 'accounts/auth/iniciar_sesion.html')

def signup_view(request):
    """Registro de usuarios con rol y cuenta inactiva."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = (request.POST.get('username') or "").strip()
        email = (request.POST.get('email') or "").strip()
        password = request.POST.get('password') or ""
        confirm_password = request.POST.get('confirm_password') or ""
        role_name = request.POST.get('role', 'Trabajador')

        context = {"username": username, "email": email}

        if not username or not email or not password or not confirm_password:
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'accounts/auth/registro.html', context)

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'accounts/auth/registro.html', context)

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'accounts/auth/registro.html', context)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya estás registrado.')
            return render(request, 'accounts/auth/registro.html', context)

        try:
            validate_password(password, user=User(username=username, email=email))
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return render(request, 'accounts/auth/registro.html', context)

        try:
            _ensure_roles_exist()

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_active = False
            user.save()

            try:
                group = Group.objects.get(name=role_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass

            messages.success(
                request,
                'Cuenta creada. Un administrador debe habilitar tu acceso.'
            )
            return redirect('signin')

        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                if "username" in str(e):
                    messages.error(request, "El nombre de usuario ya está en uso. Por favor, elige otro.")
                elif "email" in str(e):
                    messages.error(request, "El correo electrónico ya está registrado.")
                else:
                    messages.error(request, "Ya existe una cuenta con estos datos.")
            else:
                messages.error(request, "Ocurrió un error de integridad al crear la cuenta.")
            return render(request, 'accounts/auth/registro.html', context)

        except Exception as e:
            messages.error(request, f"Error inesperado al crear la cuenta. Intenta de nuevo.")
            return render(request, 'accounts/auth/registro.html', context)

    return render(request, 'accounts/auth/registro.html')

@login_required(login_url='signin')
def signout_view(request):
    """Cerrar sesión."""
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect('signin')

# PANEL INTERNO
@login_required(login_url='signin')
def admin_users_view(request):
    """Panel interno desactivado porque la plantilla se maneja desde urbix."""
    messages.info(request, "El panel de administración aún no está disponible desde accounts.")
    return redirect('home')

# PÁGINAS DINÁMICAS
@login_required(login_url='signin')
def dynamic_view(request, page):
    """Renderizar páginas dinámicas."""
    from django.http import HttpResponseNotFound
    
    if '..' in page or page.startswith('/'):
        return render(request, "error.html", status=404)

    if not page.endswith(".html"):
        template_name = f"{page}.html"
    else:
        template_name = page

    try:
        return render(request, template_name)
    except TemplateDoesNotExist:
        return render(request, "error.html", status=404)

# PERFIL (migrado de app perfil)
@login_required(login_url='signin')
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile/perfil.html", {"user": request.user, "profile": profile})

@login_required(login_url="signin")
def edit_profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        image = request.FILES.get("image")
        remove_image = request.POST.get("remove_image") == "1"

        has_name_change = first_name != (user.first_name or "")
        has_lastname_change = last_name != (user.last_name or "")
        has_phone_change = phone != (profile.phone or "")
        has_image_change = bool(image) or remove_image
        if not (has_name_change or has_lastname_change or has_phone_change or has_image_change):
            messages.info(request, "No se realizaron cambios.")
            return redirect("profile")

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        profile.phone = phone
        if remove_image:
            if profile.image:
                profile.image.delete(save=False)
            profile.image = None
            messages.success(request, "Foto de perfil eliminada.")
        elif image:
            profile.image = image
            messages.success(request, "Perfil actualizado correctamente.")
        else:
            messages.success(request, "Perfil actualizado correctamente.")
        profile.save()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})
        return redirect("profile")
    return render(request, "accounts/profile/editar_perfil.html", {"profile": profile})

def _setup_password_change_form(form):
    field_config = {
        "old_password": {"placeholder": "Ingresa tu contraseña actual", "autocomplete": "current-password"},
        "new_password1": {"placeholder": "Ingresa tu nueva contraseña", "autocomplete": "new-password"},
        "new_password2": {"placeholder": "Confirma tu nueva contraseña", "autocomplete": "new-password"},
    }

    for name, attrs in field_config.items():
        field = form.fields.get(name)
        if not field:
            continue

        widget_attrs = field.widget.attrs
        widget_attrs["class"] = "form-control"
        widget_attrs["placeholder"] = attrs["placeholder"]
        widget_attrs["autocomplete"] = attrs["autocomplete"]

@login_required(login_url='signin')
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        _setup_password_change_form(form)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Contraseña actualizada con éxito.",
                        "redirect": reverse("profile"),
                    }
                )
            messages.success(request, "La contraseña se ha actualizado correctamente.")
            return redirect("profile")
        else:
            message = "Por favor corrige los errores del formulario."
            errors_json = form.errors.get_json_data()
            # Usa los mensajes del validador nativo de contraseñas de Django como respuesta principal
            for field_errors in errors_json.values():
                if field_errors:
                    message = field_errors[0].get("message", message)
                    break
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": False,
                        "message": message,
                        "errors": errors_json,
                    },
                    status=400,
                )
            messages.error(request, message)
    else:
        form = PasswordChangeForm(user=request.user)
        _setup_password_change_form(form)
    return render(request, "accounts/profile/cambiar_contrasena.html", {"form": form})
