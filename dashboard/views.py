import logging

from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from usuarios.mixins import JefeRequiredMixin
from territorio.models import Parcela
from dashboard.aggregation import resumen_parcela, COLORES
from dashboard.kpis import calcular_kpis
from encuestas.models import Familia

# Auditoría de acceso a datos sensibles (Ley 25.326).
auditoria = logging.getLogger("auditoria")

# Marca en la sesión de que el Jefe aceptó la advertencia legal.
ADVERTENCIA_SESSION_KEY = "advertencia_datos_aceptada"


class Dashboard(JefeRequiredMixin, View):
    def get(self, request):
        datos = [{"parcela": p, "resumen": resumen_parcela(p)}
                 for p in Parcela.objects.all()]
        kpis = calcular_kpis()
        return render(request, "dashboard/dashboard.html", {
            "parcelas_resumen": datos,
            "colores": COLORES,
            "kpis": kpis,
            "advertencia_aceptada": bool(request.session.get(ADVERTENCIA_SESSION_KEY)),
        })


class AceptarAdvertencia(JefeRequiredMixin, View):
    """Registra la aceptación de la advertencia legal una vez por sesión."""

    def post(self, request):
        request.session[ADVERTENCIA_SESSION_KEY] = True
        auditoria.info(
            "ACCESO_DATOS_SENSIBLES — aceptación de advertencia legal (Ley 25.326) "
            "por jefe de campaña '%s'.",
            request.user.username,
        )
        return JsonResponse({"ok": True})


class DetalleParcela(JefeRequiredMixin, View):
    def get(self, request, numero):
        # El JOIN nominal (Familia + Voto + contacto) solo se revela si el Jefe
        # aceptó la advertencia legal en esta sesión. Enforcement de backend:
        # no alcanza con el modal del frontend.
        if not request.session.get(ADVERTENCIA_SESSION_KEY):
            return HttpResponseForbidden(
                "Debe aceptar la advertencia legal antes de acceder a datos nominales."
            )
        parcela = get_object_or_404(Parcela, numero=numero)
        familias = (Familia.objects.filter(parcela=parcela)
                    .select_related("voto", "cargada_por").order_by("nombre_familia"))
        auditoria.info(
            "ACCESO_DATOS_SENSIBLES — jefe '%s' consultó el detalle nominal de la "
            "cuadra %s (%s familias).",
            request.user.username, numero, familias.count(),
        )
        return render(request, "dashboard/_detalle.html",
                      {"parcela": parcela, "familias": familias})
