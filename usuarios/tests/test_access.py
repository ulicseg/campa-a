from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario


def make_user(username, rol):
    u = User.objects.create_user(username, password="x")
    PerfilUsuario.objects.create(user=u, rol=rol)
    return u


class RedirectTest(TestCase):
    def test_jefe_redirected_to_dashboard(self):
        make_user("jefe", PerfilUsuario.ROL_JEFE)
        self.client.login(username="jefe", password="x")
        resp = self.client.get("/", follow=False)
        self.assertRedirects(resp, "/dashboard/", target_status_code=200)

    def test_encuestador_redirected_to_cargar(self):
        make_user("ana", PerfilUsuario.ROL_ENCUESTADOR)
        self.client.login(username="ana", password="x")
        resp = self.client.get("/", follow=False)
        self.assertRedirects(resp, "/encuestas/cargar/", target_status_code=200)
