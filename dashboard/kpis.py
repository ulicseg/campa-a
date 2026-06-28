# dashboard/kpis.py
from django.db.models import Count, Sum
from territorio.models import Parcela
from encuestas.models import Familia, Voto
from dashboard.aggregation import resumen_parcela, ORDEN_DESEMPATE

def calcular_kpis():
    distribucion = {c: 0 for c in ORDEN_DESEMPATE}
    for row in Voto.objects.values("intencion").annotate(n=Count("id")):
        distribucion[row["intencion"]] = row["n"]
    parcelas = list(Parcela.objects.all())
    relevadas = sum(1 for p in parcelas if resumen_parcela(p)["total"] > 0)
    indecisas = sum(1 for p in parcelas if resumen_parcela(p)["mayoria"] == "Indeciso")
    return {
        "total_familias": Familia.objects.count(),
        "total_personas": Familia.objects.aggregate(s=Sum("integrantes"))["s"] or 0,
        "parcelas_relevadas": relevadas,
        "total_parcelas": len(parcelas),
        "distribucion": distribucion,
        "cuadras_indecisas": indecisas,
    }
