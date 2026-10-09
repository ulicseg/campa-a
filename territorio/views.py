from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from territorio.forms import AsignarParcelasForm, BarrioForm
from territorio.models import Barrio, Parcela
from usuarios.mixins import JefeRequiredMixin


def _volver_a(barrio_pk):
    return redirect(f"{reverse('lista_barrios')}?barrio={barrio_pk}")


class ListaBarrios(JefeRequiredMixin, View):
    """Pantalla única: lista de barrios + mapa donde se asignan las manzanas."""

    def _render(self, request, form):
        barrios = list(Barrio.objects.all())
        ids = {b.pk for b in barrios}
        try:
            seleccionado = int(request.GET.get("barrio", ""))
        except ValueError:
            seleccionado = None
        if seleccionado not in ids:
            seleccionado = barrios[0].pk if barrios else None
        datos = {
            "barrios": [{"id": b.pk, "nombre": b.nombre} for b in barrios],
            "parcelas": [
                {
                    "id": p.pk,
                    "numero": p.numero,
                    "points": p.svg_points,
                    "barrio": p.barrio_id,
                }
                for p in Parcela.objects.all()
            ],
            "seleccionado": seleccionado,
        }
        return render(request, "territorio/barrios.html", {"form": form, "datos": datos})

    def get(self, request):
        return self._render(request, BarrioForm())

    def post(self, request):
        form = BarrioForm(request.POST)
        if form.is_valid():
            barrio = form.save()
            messages.success(request, f"Barrio {barrio.nombre} creado. Ahora marque sus manzanas en el mapa.")
            return _volver_a(barrio.pk)
        return self._render(request, form)


class EditarBarrio(JefeRequiredMixin, View):
    """Guarda las manzanas de un barrio. La edición se hace en la lista."""

    def get(self, request, pk):
        return _volver_a(get_object_or_404(Barrio, pk=pk).pk)

    def post(self, request, pk):
        barrio = get_object_or_404(Barrio, pk=pk)
        form = AsignarParcelasForm(request.POST, barrio=barrio)
        if form.is_valid():
            form.save()
            messages.success(request, f"Se guardaron las manzanas de {barrio.nombre}.")
        else:
            messages.error(request, "No se pudo guardar: alguna manzana no existe. Recargue la página.")
        return _volver_a(barrio.pk)


class BorrarBarrio(JefeRequiredMixin, View):
    def post(self, request, pk):
        barrio = get_object_or_404(Barrio, pk=pk)
        nombre = barrio.nombre
        barrio.delete()  # SET_NULL: sus manzanas quedan sin barrio
        messages.success(request, f"Barrio {nombre} eliminado. Sus manzanas quedaron sin barrio.")
        return redirect("lista_barrios")
