from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela
from encuestas.models import Familia
from encuestas.services import crear_relevamiento


class GestionTest(TestCase):
    def setUp(self):
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")
        self.jefe = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=self.jefe, rol="jefe")

    def _crear_encuestador(self, username="ana"):
        u = User.objects.create_user(username, password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        return u

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

    def test_jefe_deletes_encuestador_without_cargas(self):
        u = self._crear_encuestador()
        self.client.login(username="jefe", password="x")
        resp = self.client.post(f"/usuarios/encuestadores/{u.pk}/borrar/")
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(User.objects.filter(pk=u.pk).exists())
        self.assertFalse(PerfilUsuario.objects.filter(user_id=u.pk).exists())

    def test_cannot_delete_encuestador_with_cargas(self):
        u = self._crear_encuestador()
        crear_relevamiento(
            datos_familia={"numero_familia": "1", "nombre_familia": "Pérez",
                           "integrantes": 2, "consentimiento_informado": True},
            intencion="PJ", parcela=self.p, usuario=u)
        self.client.login(username="jefe", password="x")
        self.client.post(f"/usuarios/encuestadores/{u.pk}/borrar/")
        self.assertTrue(User.objects.filter(pk=u.pk).exists())
        self.assertEqual(Familia.objects.count(), 1)

    def test_encuestador_cannot_delete(self):
        victima = self._crear_encuestador("victima")
        atacante = self._crear_encuestador("atacante")
        self.client.login(username="atacante", password="x")
        resp = self.client.post(f"/usuarios/encuestadores/{victima.pk}/borrar/")
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(User.objects.filter(pk=victima.pk).exists())
