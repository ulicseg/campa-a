from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from territorio.forms import AsignarParcelasForm, BarrioForm
from territorio.models import Barrio, Parcela
from usuarios.mixins import JefeRequiredMixin


class ListaBarrios(JefeRequiredMixin, View):
    def _render(self, request, form):
        return render(request, "territorio/barrios.html", {
            "form": form,
            "barrios": Barrio.objects.prefetch_related("parcelas"),
            "sin_barrio": Parcela.objects.filter(barrio__isnull=True),
        })

    def get(self, request):
        return self._render(request, BarrioForm())

    def post(self, request):
        form = BarrioForm(request.POST)
        if form.is_valid():
            barrio = form.save()
            messages.success(request, f"Barrio {barrio.nombre} creado.")
            return redirect("editar_barrio", pk=barrio.pk)
        return self._render(request, form)


class EditarBarrio(JefeRequiredMixin, View):
    def _render(self, request, barrio, form):
        return render(request, "territorio/editar_barrio.html", {
            "barrio": barrio,
            "form": form,
        })

    def get(self, request, pk):
        barrio = get_object_or_404(Barrio, pk=pk)
        return self._render(request, barrio, AsignarParcelasForm(barrio=barrio))

    def post(self, request, pk):
        barrio = get_object_or_404(Barrio, pk=pk)
        form = AsignarParcelasForm(request.POST, barrio=barrio)
        if form.is_valid():
            form.save()
            messages.success(request, f"Manzanas de {barrio.nombre} guardadas.")
            return redirect("lista_barrios")
        return self._render(request, barrio, form)


class BorrarBarrio(JefeRequiredMixin, View):
    def post(self, request, pk):
        barrio = get_object_or_404(Barrio, pk=pk)
        nombre = barrio.nombre
        barrio.delete()  # SET_NULL: sus manzanas quedan sin barrio
        messages.success(request, f"Barrio {nombre} eliminado.")
        return redirect("lista_barrios")
