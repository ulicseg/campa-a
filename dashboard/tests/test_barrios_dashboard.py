# dashboard/tests/test_barrios_dashboard.py
from django.contrib.auth.models import User
from django.test import TestCase

from dashboard.aggregation import resumen_barrio
from encuestas.services import crear_relevamiento
from territorio.models import Barrio, Parcela
from usuarios.models import PerfilUsuario


class BarriosDashboardTest(TestCase):
    def setUp(self):
        Barrio.objects.all().delete()  # la migración 0003 precarga barrios
        self.centro = Barrio.objects.create(nombre="Centro")
        self.vacio = Barrio.objects.create(nombre="Sin cuadras")
        self.p1 = Parcela.objects.create(numero=1, coords="0,0,10,0,10,10", barrio=self.centro)
        self.p2 = Parcela.objects.create(numero=2, coords="20,20,30,20,30,30", barrio=self.centro)
        self.p3 = Parcela.objects.create(numero=3, coords="50,50,60,50,60,60")
        self.u = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=self.u, rol="jefe")

    def _voto(self, parcela, intencion, integrantes=1):
        crear_relevamiento(
            datos_familia={"numero_familia": "1", "nombre_familia": "X",
                           "integrantes": integrantes, "consentimiento_informado": True},
            intencion=intencion, parcela=parcela, usuario=self.u)

    def test_resumen_barrio_suma_sus_manzanas(self):
        self._voto(self.p1, "PJ", 3)
        self._voto(self.p2, "PJ", 2)
        self._voto(self.p2, "UCR", 1)
        self._voto(self.p3, "UCR", 4)  # fuera del barrio
        r = resumen_barrio(self.centro)
        self.assertEqual(r["total"], 3)
        self.assertEqual(r["personas"], 6)
        self.assertEqual(r["mayoria"], "PJ")
        self.assertEqual(r["porcentaje"], 67)
        self.assertEqual(r["distribucion"]["UCR"], 1)

    def test_resumen_barrio_vacio(self):
        r = resumen_barrio(self.vacio)
        self.assertEqual(r["total"], 0)
        self.assertIsNone(r["mayoria"])

    def test_dashboard_muestra_barrios(self):
        self._voto(self.p1, "PJ")
        self.client.login(username="jefe", password="x")
        resp = self.client.get("/dashboard/")
        self.assertContains(resp, 'id="sel-barrio"')
        self.assertContains(resp, 'class="barrio-label"', count=1)  # el vacío no tiene etiqueta
        barrios = {b["nombre"]: b for b in resp.context["barrios"]}
        self.assertEqual(barrios["Centro"]["relevadas"], 1)
        self.assertEqual(len(barrios["Centro"]["manzanas"]), 2)
        self.assertEqual(barrios["Sin cuadras"]["manzanas"], [])

    def test_dashboard_sin_barrios_no_muestra_selector(self):
        Barrio.objects.all().delete()
        self.client.login(username="jefe", password="x")
        self.assertNotContains(self.client.get("/dashboard/"), 'id="sel-barrio"')
