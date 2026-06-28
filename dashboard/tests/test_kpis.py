# dashboard/tests/test_kpis.py
from django.test import TestCase
from django.contrib.auth.models import User
from territorio.models import Parcela
from encuestas.services import crear_relevamiento
from dashboard.kpis import calcular_kpis


class KpisTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("ana", password="x")
        self.p1 = Parcela.objects.create(numero=1, coords="1,2,3,4")
        self.p2 = Parcela.objects.create(numero=2, coords="1,2,3,4")

    def _voto(self, parcela, intencion, integrantes=2):
        crear_relevamiento(
            datos_familia={"numero_familia": "1", "nombre_familia": "X",
                           "integrantes": integrantes, "consentimiento_informado": True},
            intencion=intencion, parcela=parcela, usuario=self.u)

    def test_kpis_totals_and_coverage(self):
        self._voto(self.p1, "PJ", 3)
        self._voto(self.p1, "UCR", 2)
        k = calcular_kpis()
        self.assertEqual(k["total_familias"], 2)
        self.assertEqual(k["total_personas"], 5)
        self.assertEqual(k["parcelas_relevadas"], 1)
        self.assertEqual(k["total_parcelas"], 2)
        self.assertEqual(k["distribucion"]["PJ"], 1)

    def test_cuadras_indecisas_counts_majority_indeciso(self):
        self._voto(self.p2, "Indeciso")
        self.assertEqual(calcular_kpis()["cuadras_indecisas"], 1)
