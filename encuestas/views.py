# encuestas/views.py
from django.shortcuts import render, redirect
from django.views import View

from usuarios.mixins import EncuestadorRequiredMixin
from encuestas.forms import FamiliaForm
from encuestas.services import crear_relevamiento


class CargarFamilia(EncuestadorRequiredMixin, View):
    def _parcelas(self, request):
        return request.user.perfil.parcelas.all()

    def get(self, request):
        form = FamiliaForm(parcelas_qs=self._parcelas(request))
        return render(request, "encuestas/cargar.html", {"form": form})

    def post(self, request):
        form = FamiliaForm(request.POST, parcelas_qs=self._parcelas(request))
        if form.is_valid():
            cd = form.cleaned_data
            crear_relevamiento(
                datos_familia={k: cd[k] for k in (
                    "numero_familia", "nombre_familia", "integrantes",
                    "contacto_1", "contacto_2", "consentimiento_informado",
                )},
                intencion=cd["intencion"],
                parcela=cd["parcela"],
                usuario=request.user,
            )
            return redirect("mis_cargas")
        return render(request, "encuestas/cargar.html", {"form": form})
