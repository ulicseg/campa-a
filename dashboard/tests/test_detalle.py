# dashboard/tests/test_detalle.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela
from encuestas.services import crear_relevamiento


class DetalleTest(TestCase):
    def setUp(self):
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")
        self.jefe = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=self.jefe, rol="jefe")
        crear_relevamiento(
            datos_familia={"numero_familia": "1", "nombre_familia": "Pérez",
                           "integrantes": 3, "contacto_1": "3624-111",
                           "consentimiento_informado": True},
            intencion="PJ", parcela=self.p, usuario=self.jefe)

    def test_detalle_shows_nominal_join(self):
        self.client.login(username="jefe", password="x")
        resp = self.client.get("/dashboard/parcela/12/detalle/")
        self.assertContains(resp, "Pérez")
        self.assertContains(resp, "3624-111")
        self.assertContains(resp, "PJ")

    def test_encuestador_gets_403(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self.client.get("/dashboard/parcela/12/detalle/").status_code, 403)
