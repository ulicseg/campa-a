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

    def _aceptar(self):
        return self.client.post("/dashboard/aceptar-advertencia/")

    def test_detalle_blocked_until_warning_accepted(self):
        self.client.login(username="jefe", password="x")
        # Sin aceptar la advertencia legal, los datos nominales no se revelan.
        self.assertEqual(self.client.get("/dashboard/parcela/12/detalle/").status_code, 403)

    def test_detalle_shows_nominal_join_after_accept(self):
        self.client.login(username="jefe", password="x")
        self._aceptar()
        resp = self.client.get("/dashboard/parcela/12/detalle/")
        self.assertContains(resp, "Pérez")
        self.assertContains(resp, "3624-111")
        self.assertContains(resp, "PJ")

    def test_accept_sets_session_flag(self):
        self.client.login(username="jefe", password="x")
        resp = self._aceptar()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.client.session.get("advertencia_datos_aceptada"))

    def test_encuestador_cannot_view_detalle(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self.client.get("/dashboard/parcela/12/detalle/").status_code, 403)

    def test_encuestador_cannot_accept(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self._aceptar().status_code, 403)

    def test_logout_clears_acceptance(self):
        self.client.login(username="jefe", password="x")
        self._aceptar()
        self.client.post("/accounts/logout/")
        self.client.login(username="jefe", password="x")
        # Tras un nuevo login la advertencia debe volver a exigirse.
        self.assertEqual(self.client.get("/dashboard/parcela/12/detalle/").status_code, 403)
