# dashboard/tests/test_dashboard.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela
from encuestas.services import crear_relevamiento


class DashboardTest(TestCase):
    def setUp(self):
        Parcela.objects.create(numero=12, coords="10,20,30,40,50,60")
        self.jefe = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=self.jefe, rol="jefe")

    def test_encuestador_gets_403(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self.client.get("/dashboard/").status_code, 403)

    def test_jefe_sees_polygon_points(self):
        self.client.login(username="jefe", password="x")
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "10,20 30,40 50,60")
        self.assertContains(resp, "<polygon")
