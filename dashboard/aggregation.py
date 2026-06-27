# dashboard/aggregation.py
from django.db.models import Count
from encuestas.models import Voto

COLORES = {
    "PJ": "#1f4e9c",
    "UCR": "#c62828",
    "Otro": "#2e7d32",
    "Indeciso": "#757575",
    "No contesta": "#e0e0e0",
}
ORDEN_DESEMPATE = ["PJ", "UCR", "Otro", "Indeciso", "No contesta"]


def resumen_parcela(parcela):
    counts = {
        row["intencion"]: row["n"]
        for row in (
            Voto.objects.filter(familia__parcela=parcela)
            .values("intencion")
            .annotate(n=Count("id"))
        )
    }
    total = sum(counts.values())
    if total == 0:
        return {
            "numero": parcela.numero,
            "total": 0,
            "mayoria": None,
            "color": None,
            "opacidad": 0,
            "porcentaje": 0,
        }
    max_n = max(counts.values())
    mayoria = next(c for c in ORDEN_DESEMPATE if counts.get(c, 0) == max_n)
    frac = max_n / total
    return {
        "numero": parcela.numero,
        "total": total,
        "mayoria": mayoria,
        "color": COLORES[mayoria],
        "opacidad": round(max(0.35, frac), 2),
        "porcentaje": round(frac * 100),
    }
