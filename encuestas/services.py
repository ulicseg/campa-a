# encuestas/services.py
from django.db import transaction
from encuestas.models import Familia, Voto


@transaction.atomic
def crear_relevamiento(*, datos_familia, intencion, parcela, usuario):
    familia = Familia.objects.create(parcela=parcela, cargada_por=usuario, **datos_familia)
    Voto.objects.create(familia=familia, intencion=intencion)
    return familia
