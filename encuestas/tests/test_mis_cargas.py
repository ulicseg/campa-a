# encuestas/tests/test_mis_cargas.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela
from encuestas.services import crear_relevamiento
from encuestas.models import Familia


class MisCargasTest(TestCase):
    def setUp(self):
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")
        self.ana = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=self.ana, rol="encuestador").parcelas.add(self.p)
        self.beto = User.objects.create_user("beto", password="x")
        PerfilUsuario.objects.create(user=self.beto, rol="encuestador").parcelas.add(self.p)

    def _fam(self, user):
        return crear_relevamiento(
            datos_familia={"numero_familia": "1", "nombre_familia": "X",
                           "integrantes": 2, "consentimiento_informado": True},
            intencion="PJ", parcela=self.p, usuario=user)

    def test_list_shows_only_own(self):
        self._fam(self.ana); self._fam(self.beto)
        self.client.login(username="ana", password="x")
        resp = self.client.get("/encuestas/mias/")
        self.assertEqual(len(resp.context["familias"]), 1)

    def test_cannot_delete_others(self):
        fam = self._fam(self.beto)
        self.client.login(username="ana", password="x")
        resp = self.client.post(f"/encuestas/{fam.pk}/borrar/")
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Familia.objects.filter(pk=fam.pk).exists())
