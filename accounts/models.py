from django.db import models
from django.conf import settings

class Profile(models.Model):
    """Perfil básico del usuario."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")
    image = models.ImageField(upload_to="profile_uploads/", blank=True, null=True, verbose_name="Imagen de perfil")

    class Meta:
        db_table = "account_profile"
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return self.user.get_username()
