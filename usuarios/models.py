from django.contrib.auth.models import User
from django.db import models
from territorio.models import Parcela

class PerfilUsuario(models.Model):
    ROL_ENCUESTADOR = "encuestador"
    ROL_JEFE = "jefe"
    ROLES = [(ROL_ENCUESTADOR, "Encuestador"), (ROL_JEFE, "Jefe de Campaña")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=ROLES)
    parcelas = models.ManyToManyField(Parcela, blank=True, related_name="encuestadores")

    @property
    def es_jefe(self):
        return self.rol == self.ROL_JEFE

    @property
    def es_encuestador(self):
        return self.rol == self.ROL_ENCUESTADOR

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"
