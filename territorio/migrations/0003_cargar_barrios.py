from django.db import migrations

BARRIOS = [
    "10 Viviendas (BETO PEREZ)",
    "15 Viviendas Fibramalba",
    "19 Viviendas (HERMOSI)",
    "20 Viviendas (CEMENTERIO)",
    "20 Viviendas (TORO MIRANDA)",
    "25 Viviendas (B.O.)",
    "Abelino Flores",
    "Barrio San Justo",
    "Barrio Sur",
    "Centro",
    "CIAVA",
    "CTI",
    "El Pastizal (GLAVAS COMERCIO)",
    "Ex Playa del Ferrocarril",
    "FO.NA.VI",
    "Grioni",
    "Instituto (CACHO-MAXI)",
    "Lote X (GARCETE LEGUA D)",
    "Madres Solteras",
    "Matadero",
    "Néstor Kirchner (25 VIVIENDAS)",
    "Obrero (3 CALLES. ROM.POL.CARRE)",
    "Rincón Dichoso (MIERES-BLANCO)",
    "Santa Ana",
    "Santa Teresita (PIPA-GARCETE)",
    "ROTONDA, ruta 9 y 7",
]


def cargar(apps, schema_editor):
    Barrio = apps.get_model("territorio", "Barrio")
    for nombre in BARRIOS:
        Barrio.objects.get_or_create(nombre=nombre)


def descargar(apps, schema_editor):
    Barrio = apps.get_model("territorio", "Barrio")
    Barrio.objects.filter(nombre__in=BARRIOS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("territorio", "0002_barrio"),
    ]

    operations = [
        migrations.RunPython(cargar, descargar),
    ]
