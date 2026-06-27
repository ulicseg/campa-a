# encuestas/tests/test_cargar.py
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela
from encuestas.models import Familia, Voto


class CargarTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("ana", password="x")
        self.perfil = PerfilUsuario.objects.create(user=self.u, rol=PerfilUsuario.ROL_ENCUESTADOR)
        self.p_mia = Parcela.objects.create(numero=12, coords="1,2,3,4")
        self.p_ajena = Parcela.objects.create(numero=40, coords="1,2,3,4")
        self.perfil.parcelas.add(self.p_mia)
        self.client.login(username="ana", password="x")

    def _payload(self, **over):
        data = {"numero_familia": "5", "nombre_familia": "Pérez", "integrantes": 4,
                "contacto_1": "", "contacto_2": "", "parcela": self.p_mia.id,
                "intencion": "PJ", "consentimiento_informado": "on"}
        data.update(over); return data

    def test_saves_with_consent(self):
        resp = self.client.post("/encuestas/cargar/", self._payload())
        self.assertEqual(Familia.objects.count(), 1)
        self.assertEqual(Voto.objects.get().intencion, "PJ")

    def test_rejects_without_consent(self):
        data = self._payload(); data.pop("consentimiento_informado")
        self.client.post("/encuestas/cargar/", data)
        self.assertEqual(Familia.objects.count(), 0)

    def test_cannot_load_into_unassigned_parcela(self):
        self.client.post("/encuestas/cargar/", self._payload(parcela=self.p_ajena.id))
        self.assertEqual(Familia.objects.count(), 0)
