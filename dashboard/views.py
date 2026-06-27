from django.shortcuts import render, get_object_or_404
from django.views import View
from usuarios.mixins import JefeRequiredMixin
from territorio.models import Parcela
from dashboard.aggregation import resumen_parcela, COLORES
from encuestas.models import Familia


class Dashboard(JefeRequiredMixin, View):
    def get(self, request):
        datos = [{"parcela": p, "resumen": resumen_parcela(p)}
                 for p in Parcela.objects.all()]
        return render(request, "dashboard/dashboard.html",
                      {"parcelas_resumen": datos, "colores": COLORES})


class DetalleParcela(JefeRequiredMixin, View):
    def get(self, request, numero):
        parcela = get_object_or_404(Parcela, numero=numero)
        familias = (Familia.objects.filter(parcela=parcela)
                    .select_related("voto", "cargada_por").order_by("nombre_familia"))
        return render(request, "dashboard/_detalle.html",
                      {"parcela": parcela, "familias": familias})
