from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from territorio.models import Parcela
from usuarios.models import PerfilUsuario


class CrearCuentasParcelasTest(TestCase):
    def setUp(self):
        for n in (1, 2, 3):
            Parcela.objects.create(numero=n, coords="0,0,1,1,2,2")

    def test_crea_una_cuenta_por_parcela(self):
        call_command("crear_cuentas_parcelas")
        for n in (1, 2, 3):
            user = User.objects.get(username=f"parcela{n}")
            self.assertTrue(user.check_password(f"parcela{n}"))
            self.assertEqual(user.perfil.rol, PerfilUsuario.ROL_ENCUESTADOR)
            self.assertEqual(
                list(user.perfil.parcelas.values_list("numero", flat=True)), [n]
            )

    def test_idempotente(self):
        call_command("crear_cuentas_parcelas")
        call_command("crear_cuentas_parcelas")
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(PerfilUsuario.objects.count(), 3)

    def test_login_funciona(self):
        call_command("crear_cuentas_parcelas")
        self.assertTrue(self.client.login(username="parcela2", password="parcela2"))
