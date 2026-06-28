from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User


class CrearJefeCommandTest(TestCase):
    def test_creates_jefe_superuser(self):
        call_command("crear_jefe", "lider", "--password", "secreta123")
        u = User.objects.get(username="lider")
        self.assertTrue(u.is_superuser)
        self.assertTrue(u.is_staff)
        self.assertTrue(u.perfil.es_jefe)
        self.assertTrue(u.check_password("secreta123"))

    def test_idempotent_updates_password(self):
        call_command("crear_jefe", "lider", "--password", "uno12345")
        call_command("crear_jefe", "lider", "--password", "dos12345")
        self.assertEqual(User.objects.filter(username="lider").count(), 1)
        self.assertTrue(User.objects.get(username="lider").check_password("dos12345"))
