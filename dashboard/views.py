import logging

from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from usuarios.mixins import JefeRequiredMixin
from territorio.models import Barrio, Parcela
from dashboard.aggregation import resumen_barrio, resumen_parcela, COLORES
from dashboard.kpis import calcular_kpis
from dashboard.pdf import generar_pdf
from encuestas.models import Familia

# Auditoría de acceso a datos sensibles (Ley 25.326).
auditoria = logging.getLogger("auditoria")

# Marca en la sesión de que el Jefe aceptó la advertencia legal.
ADVERTENCIA_SESSION_KEY = "advertencia_datos_aceptada"


def _centro(parcelas):
    """Promedio de los vértices de las manzanas: dónde va la etiqueta del barrio."""
    xs, ys = [], []
    for p in parcelas:
        nums = [float(n) for n in p.coords.split(",") if n.strip()]
        xs += nums[0::2]
        ys += nums[1::2]
    if not xs:
        return None
    return [round(sum(xs) / len(xs)), round(sum(ys) / len(ys))]


def _barrios_resumen(datos):
    """Resumen agregado por barrio (sin datos nominales) para el mapa y el panel."""
    por_barrio = {}
    for item in datos:
        if item["parcela"].barrio_id:
            por_barrio.setdefault(item["parcela"].barrio_id, []).append(item)
    barrios = []
    for b in Barrio.objects.all():
        items = por_barrio.get(b.pk, [])
        r = resumen_barrio(b)
        r.update({
            "id": b.pk,
            "nombre": b.nombre,
            "centro": _centro([i["parcela"] for i in items]),
            "manzanas": [i["resumen"] for i in items],
            "relevadas": sum(1 for i in items if i["resumen"]["total"]),
        })
        barrios.append(r)
    return barrios


class Dashboard(JefeRequiredMixin, View):
    def get(self, request):
        datos = [{"parcela": p, "resumen": resumen_parcela(p)}
                 for p in Parcela.objects.select_related("barrio")]
        kpis = calcular_kpis()
        return render(request, "dashboard/dashboard.html", {
            "parcelas_resumen": datos,
            "barrios": _barrios_resumen(datos),
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


def _familias_de(parcela):
    return list(Familia.objects.filter(parcela=parcela)
                .select_related("voto", "cargada_por").order_by("nombre_familia"))


def _respuesta_pdf(contenido, nombre):
    resp = HttpResponse(contenido, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{nombre}"'
    return resp


class PdfParcela(JefeRequiredMixin, View):
    """PDF de una manzana. Mismo control que el detalle nominal."""

    def get(self, request, numero):
        if not request.session.get(ADVERTENCIA_SESSION_KEY):
            return HttpResponseForbidden(
                "Debe aceptar la advertencia legal antes de acceder a datos nominales.")
        parcela = get_object_or_404(Parcela, numero=numero)
        familias = _familias_de(parcela)
        auditoria.info(
            "ACCESO_DATOS_SENSIBLES — jefe '%s' generó el PDF de la cuadra %s (%s familias).",
            request.user.username, numero, len(familias),
        )
        pdf = generar_pdf(f"Manzana {numero}", [(parcela, familias)], request.user.username,
                          subtitulo=f"Barrio {parcela.barrio.nombre}" if parcela.barrio else None)
        return _respuesta_pdf(pdf, f"manzana-{numero}.pdf")


class PdfBarrio(JefeRequiredMixin, View):
    """PDF de un barrio con los datos de todas sus manzanas."""

    def get(self, request, pk):
        if not request.session.get(ADVERTENCIA_SESSION_KEY):
            return HttpResponseForbidden(
                "Debe aceptar la advertencia legal antes de acceder a datos nominales.")
        barrio = get_object_or_404(Barrio, pk=pk)
        bloques = [(p, _familias_de(p)) for p in barrio.parcelas.all()]
        auditoria.info(
            "ACCESO_DATOS_SENSIBLES — jefe '%s' generó el PDF del barrio '%s' "
            "(%s manzanas, %s familias).",
            request.user.username, barrio.nombre, len(bloques), sum(len(f) for _, f in bloques),
        )
        pdf = generar_pdf(f"Barrio {barrio.nombre}", bloques, request.user.username)
        return _respuesta_pdf(pdf, f"barrio-{barrio.pk}.pdf")
