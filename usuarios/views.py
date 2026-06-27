from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View


class PostLoginRedirect(LoginRequiredMixin, View):
    def get(self, request):
        perfil = getattr(request.user, "perfil", None)
        if perfil and perfil.es_jefe:
            return redirect("dashboard")
        return redirect("cargar_familia")
