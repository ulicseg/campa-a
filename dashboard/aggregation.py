# dashboard/aggregation.py
from django.db.models import Count, Sum
from encuestas.models import Familia, Voto

COLORES = {
    "PJ": "#1f4e9c",
    "UCR": "#c62828",
    "Otro": "#2e7d32",
    "Indeciso": "#757575",
    "No contesta": "#e0e0e0",
}
ORDEN_DESEMPATE = ["PJ", "UCR", "Otro", "Indeciso", "No contesta"]


def _conteos(votos):
    return {row["intencion"]: row["n"]
            for row in votos.values("intencion").annotate(n=Count("id"))}


def _mayoria(counts):
    """Mayoría, color, opacidad y % de dominancia a partir de los conteos."""
    total = sum(counts.values())
    if total == 0:
        return {"total": 0, "mayoria": None, "color": None, "opacidad": 0, "porcentaje": 0}
    max_n = max(counts.values())
    mayoria = next(c for c in ORDEN_DESEMPATE if counts.get(c, 0) == max_n)
    frac = max_n / total
    return {
        "total": total,
        "mayoria": mayoria,
        "color": COLORES[mayoria],
        "opacidad": round(max(0.35, frac), 2),
        "porcentaje": round(frac * 100),
    }


def resumen_parcela(parcela):
    r = _mayoria(_conteos(Voto.objects.filter(familia__parcela=parcela)))
    r["numero"] = parcela.numero
    return r


def resumen_barrio(barrio):
    """Datos agregados (no nominales) de todas las manzanas de un barrio."""
    counts = _conteos(Voto.objects.filter(familia__parcela__barrio=barrio))
    r = _mayoria(counts)
    r["distribucion"] = {c: counts.get(c, 0) for c in ORDEN_DESEMPATE}
    r["personas"] = (Familia.objects.filter(parcela__barrio=barrio)
                     .aggregate(s=Sum("integrantes"))["s"] or 0)
    return r
