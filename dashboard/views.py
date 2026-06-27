from django.shortcuts import render
from django.views import View
from usuarios.mixins import JefeRequiredMixin
from territorio.models import Parcela
from dashboard.aggregation import resumen_parcela, COLORES


class Dashboard(JefeRequiredMixin, View):
    def get(self, request):
        datos = [{"parcela": p, "resumen": resumen_parcela(p)}
                 for p in Parcela.objects.all()]
        return render(request, "dashboard/dashboard.html",
                      {"parcelas_resumen": datos, "colores": COLORES})
