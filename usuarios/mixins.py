from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class _RolMixin(LoginRequiredMixin):
    rol_requerido = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        perfil = getattr(request.user, "perfil", None)
        if perfil is None or perfil.rol != self.rol_requerido:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class JefeRequiredMixin(_RolMixin):
    rol_requerido = "jefe"


class EncuestadorRequiredMixin(_RolMixin):
    rol_requerido = "encuestador"
