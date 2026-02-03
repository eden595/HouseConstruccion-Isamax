from django.contrib import admin
from django.urls import path
from . import views
from .views import (
    home_view, signin_view, signup_view, signout_view, admin_users_view, dynamic_view,
    profile_view, edit_profile_view, change_password_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('signin/', signin_view, name='signin'),
    path('signup/', signup_view, name='signup'),
    path('signout/', signout_view, name='signout'),
    path('admin-users/', admin_users_view, name='admin_users'),
    path("mi-perfil/", profile_view, name="profile"),
    path("mi-perfil/editar/", edit_profile_view, name="edit_profile"),
    path("mi-perfil/cambiar-password/", change_password_view, name="change_password"),

    path("<str:page>", dynamic_view, name="dynamic_page"),
]
