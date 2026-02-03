from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def home_view(request):
    """Vista principal - requiere autenticación"""
    if not request.user.is_authenticated:
        return redirect('signin')
    return render(request, 'index.html')


def signin_view(request):
    """Vista de inicio de sesión"""

    # Si ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('rememberMe')

        # Autenticar usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:

            # BLOQUEAR SI EL USUARIO NO ESTÁ HABILITADO
            if not user.is_active:
                messages.warning(
                    request,
                    'Haz iniciado sesión, pero tu cuenta aún no está habilitada. '
                    'Espera a que el administrador la active.'
                )
                return redirect('signin')

            # Si está habilitado → iniciar sesión
            login(request, user)
            
            # Configurar duración de sesión
            if not remember_me:
                request.session.set_expiry(0)  # Expira al cerrar navegador
            
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Nombre de usuario o contraseña inválidos.')
    
    return render(request, 'auth-signin.html')


def signup_view(request):
    """Vista de registro"""
    
    # Si ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validaciones
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'auth-signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'auth-signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'auth-signup.html')

        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'auth-signup.html')

        # Crear usuario DESHABILITADO
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_active = False  # QUEDA DESHABILITADO HASTA QUE EL ADMIN LO ACTIVE
            user.save()

            messages.success(
                request,
                '¡Cuenta creada! Un administrador debe habilitar tu cuenta antes de poder iniciar sesión.'
            )
            return redirect('signin')

        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')

    return render(request, 'auth-signup.html')


@login_required(login_url='signin')
def signout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    return render(request, 'auth-signout.html')


@login_required(login_url='signin')
def admin_users_view(request):
    """
    Panel interno para administración de usuarios (requiere ser staff/superuser).
    Permite habilitar / deshabilitar usuarios cambiando is_active.
    """

    # Restringir acceso solo a administradores
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')

    usuarios = User.objects.all().order_by('id')

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        accion = request.POST.get("accion")

        try:
            u = User.objects.get(id=user_id)

            if accion == "habilitar":
                u.is_active = True
            elif accion == "deshabilitar":
                u.is_active = False

            u.save()
            messages.success(request, f"Usuario {u.username} actualizado correctamente.")
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")

        return redirect("admin_users")

    return render(request, "users-admin.html", {"usuarios": usuarios})


@login_required(login_url='signin')
def dynamic_view(request, page):
    """Vista dinámica para renderizar cualquier template"""
    print(f"Trying to render template: {page}")
    try:
        return render(request, f"{page}")
    except TemplateDoesNotExist as e:
        print(f"Template not found: {e}")
        try:
            return render(request, "pages-404.html")
        except TemplateDoesNotExist as e2:
            print(f"404 template not found: {e2}")
            return HttpResponse("Page not found", status=404)
