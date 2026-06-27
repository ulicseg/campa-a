from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from territorio.models import Parcela

class PerfilTest(TestCase):
    def test_perfil_roles_and_parcelas(self):
        u = User.objects.create_user("ana", password="x")
        p = Parcela.objects.create(numero=12, coords="1,2,3,4")
        perfil = PerfilUsuario.objects.create(user=u, rol=PerfilUsuario.ROL_ENCUESTADOR)
        perfil.parcelas.add(p)
        self.assertTrue(perfil.es_encuestador)
        self.assertFalse(perfil.es_jefe)
        self.assertIn(p, perfil.parcelas.all())
