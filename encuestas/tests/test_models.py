# encuestas/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from territorio.models import Parcela
from encuestas.models import Familia, Voto
from encuestas.services import crear_relevamiento

class RelevamientoTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("ana", password="x")
        self.p = Parcela.objects.create(numero=12, coords="1,2,3,4")

    def test_crear_relevamiento_writes_both_tables(self):
        fam = crear_relevamiento(
            datos_familia={"numero_familia": "5", "nombre_familia": "Pérez",
                           "integrantes": 4, "consentimiento_informado": True},
            intencion="PJ", parcela=self.p, usuario=self.u,
        )
        self.assertEqual(Familia.objects.count(), 1)
        self.assertEqual(Voto.objects.count(), 1)
        self.assertEqual(fam.voto.intencion, "PJ")
        self.assertEqual(fam.cargada_por, self.u)

    def test_rollback_when_intencion_invalid(self):
        with self.assertRaises(Exception):
            crear_relevamiento(
                datos_familia={"numero_familia": "5", "nombre_familia": "Pérez",
                               "integrantes": 4, "consentimiento_informado": True},
                intencion="NO_EXISTE", parcela=self.p, usuario=self.u,
            )
        self.assertEqual(Familia.objects.count(), 0)
        self.assertEqual(Voto.objects.count(), 0)
