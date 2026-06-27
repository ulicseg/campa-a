from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View

from usuarios.forms import EncuestadorForm
from usuarios.mixins import JefeRequiredMixin
from usuarios.models import PerfilUsuario


class PostLoginRedirect(LoginRequiredMixin, View):
    def get(self, request):
        perfil = getattr(request.user, "perfil", None)
        if perfil and perfil.es_jefe:
            return redirect("dashboard")
        return redirect("cargar_familia")


class GestionEncuestadores(JefeRequiredMixin, View):
    def get(self, request):
        return render(request, "usuarios/gestion.html", {
            "form": EncuestadorForm(),
            "encuestadores": PerfilUsuario.objects.filter(
                rol=PerfilUsuario.ROL_ENCUESTADOR
            ).select_related("user"),
        })

    def post(self, request):
        form = EncuestadorForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(cd["username"], password=cd["password"])
            perfil = PerfilUsuario.objects.create(
                user=user, rol=PerfilUsuario.ROL_ENCUESTADOR
            )
            perfil.parcelas.set(cd["parcelas"])
            return redirect("gestion_encuestadores")
        return render(request, "usuarios/gestion.html", {
            "form": form,
            "encuestadores": PerfilUsuario.objects.filter(
                rol=PerfilUsuario.ROL_ENCUESTADOR
            ).select_related("user"),
        })
