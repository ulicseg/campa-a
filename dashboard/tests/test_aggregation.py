# dashboard/tests/test_aggregation.py
from django.test import TestCase
from django.contrib.auth.models import User
from territorio.models import Parcela
from encuestas.services import crear_relevamiento
from dashboard.aggregation import resumen_parcela, COLORES


class AggregationTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("ana", password="x")
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")

    def _voto(self, intencion, n=1):
        for _ in range(n):
            crear_relevamiento(
                datos_familia={"numero_familia": "1", "nombre_familia": "X",
                               "integrantes": 1, "consentimiento_informado": True},
                intencion=intencion, parcela=self.p, usuario=self.u)

    def test_empty_parcela_is_transparent(self):
        r = resumen_parcela(self.p)
        self.assertEqual(r["total"], 0)
        self.assertIsNone(r["mayoria"])
        self.assertIsNone(r["color"])
        self.assertEqual(r["opacidad"], 0)

    def test_majority_color_and_opacity(self):
        self._voto("PJ", 8)
        self._voto("UCR", 2)
        r = resumen_parcela(self.p)
        self.assertEqual(r["mayoria"], "PJ")
        self.assertEqual(r["color"], COLORES["PJ"])
        self.assertEqual(r["porcentaje"], 80)
        self.assertEqual(r["opacidad"], 0.8)

    def test_opacity_floor_is_035(self):
        self._voto("PJ", 1)
        self._voto("UCR", 1)
        self._voto("Otro", 1)
        r = resumen_parcela(self.p)  # PJ wins tie at 1/3 ≈ 0.33 -> floored
        self.assertEqual(r["opacidad"], 0.35)

    def test_tie_break_order_pj_over_ucr(self):
        self._voto("UCR", 2)
        self._voto("PJ", 2)
        self.assertEqual(resumen_parcela(self.p)["mayoria"], "PJ")
