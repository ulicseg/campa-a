from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela


class GestionTest(TestCase):
    def setUp(self):
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")
        self.jefe = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=self.jefe, rol="jefe")

    def test_encuestador_gets_403(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self.client.get("/usuarios/encuestadores/").status_code, 403)

    def test_jefe_creates_encuestador_with_parcela(self):
        self.client.login(username="jefe", password="x")
        resp = self.client.post("/usuarios/encuestadores/", {
            "username": "nuevo", "password": "secreta123", "parcelas": [self.p.id]})
        nuevo = User.objects.get(username="nuevo")
        self.assertTrue(nuevo.perfil.es_encuestador)
        self.assertIn(self.p, nuevo.perfil.parcelas.all())
