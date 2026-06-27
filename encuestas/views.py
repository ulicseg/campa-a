# encuestas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from usuarios.mixins import EncuestadorRequiredMixin
from encuestas.forms import FamiliaForm
from encuestas.models import Familia, Voto
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


class MisCargas(EncuestadorRequiredMixin, View):
    def get(self, request):
        familias = (Familia.objects.filter(cargada_por=request.user)
                    .select_related("parcela", "voto").order_by("-fecha"))
        return render(request, "encuestas/mis_cargas.html", {"familias": familias})


class BorrarFamilia(EncuestadorRequiredMixin, View):
    def post(self, request, pk):
        fam = get_object_or_404(Familia, pk=pk, cargada_por=request.user)
        fam.delete()
        return redirect("mis_cargas")


class EditarFamilia(EncuestadorRequiredMixin, View):
    def _get_fam(self, request, pk):
        return get_object_or_404(Familia, pk=pk, cargada_por=request.user)

    def get(self, request, pk):
        fam = self._get_fam(request, pk)
        form = FamiliaForm(parcelas_qs=request.user.perfil.parcelas.all(), initial={
            "numero_familia": fam.numero_familia,
            "nombre_familia": fam.nombre_familia,
            "integrantes": fam.integrantes,
            "contacto_1": fam.contacto_1,
            "contacto_2": fam.contacto_2,
            "parcela": fam.parcela_id,
            "intencion": fam.voto.intencion,
            "consentimiento_informado": True,
        })
        return render(request, "encuestas/cargar.html", {"form": form, "editar": True})

    def post(self, request, pk):
        fam = self._get_fam(request, pk)
        form = FamiliaForm(request.POST, parcelas_qs=request.user.perfil.parcelas.all())
        if form.is_valid():
            cd = form.cleaned_data
            for field in ("numero_familia", "nombre_familia", "integrantes",
                          "contacto_1", "contacto_2", "consentimiento_informado"):
                setattr(fam, field, cd[field])
            fam.parcela = cd["parcela"]
            fam.save()
            Voto.objects.update_or_create(familia=fam, defaults={"intencion": cd["intencion"]})
            return redirect("mis_cargas")
        return render(request, "encuestas/cargar.html", {"form": form, "editar": True})
