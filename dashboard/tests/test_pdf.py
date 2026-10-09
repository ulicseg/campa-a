# dashboard/tests/test_pdf.py
from django.contrib.auth.models import User
from django.test import TestCase

from encuestas.services import crear_relevamiento
from territorio.models import Barrio, Parcela
from usuarios.models import PerfilUsuario


class PdfTest(TestCase):
    def setUp(self):
        self.barrio = Barrio.objects.create(nombre="Barrio de Prueba")
        self.p1 = Parcela.objects.create(numero=1, coords="1,2,3,4", barrio=self.barrio)
        self.p2 = Parcela.objects.create(numero=2, coords="1,2,3,4", barrio=self.barrio)
        self.jefe = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=self.jefe, rol="jefe")
        for parcela, nombre in ((self.p1, "Pérez"), (self.p2, "Gómez")):
            crear_relevamiento(
                datos_familia={"numero_familia": "1", "nombre_familia": nombre,
                               "integrantes": 3, "contacto_1": "3624-111",
                               "consentimiento_informado": True},
                intencion="PJ", parcela=parcela, usuario=self.jefe)

    def _login(self, aceptar=True):
        self.client.login(username="jefe", password="x")
        if aceptar:
            self.client.post("/dashboard/aceptar-advertencia/")

    def test_pdf_parcela(self):
        self._login()
        resp = self.client.get("/dashboard/parcela/1/pdf/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertTrue(resp.content.startswith(b"%PDF"))

    def test_pdf_barrio(self):
        self._login()
        resp = self.client.get(f"/dashboard/barrio/{self.barrio.pk}/pdf/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.content.startswith(b"%PDF"))

    def test_pdf_barrio_sin_manzanas(self):
        self._login()
        vacio = Barrio.objects.create(nombre="Barrio Vacío de Prueba")
        self.assertEqual(self.client.get(f"/dashboard/barrio/{vacio.pk}/pdf/").status_code, 200)

    def test_bloqueado_sin_advertencia(self):
        self._login(aceptar=False)
        self.assertEqual(self.client.get("/dashboard/parcela/1/pdf/").status_code, 403)
        self.assertEqual(self.client.get(f"/dashboard/barrio/{self.barrio.pk}/pdf/").status_code, 403)

    def test_encuestador_no_accede(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self.client.get("/dashboard/parcela/1/pdf/").status_code, 403)
        self.assertEqual(self.client.get(f"/dashboard/barrio/{self.barrio.pk}/pdf/").status_code, 403)
