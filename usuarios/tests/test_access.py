from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.views import View
from usuarios.mixins import JefeRequiredMixin
from usuarios.models import PerfilUsuario


def make_user(username, rol):
    u = User.objects.create_user(username, password="x")
    PerfilUsuario.objects.create(user=u, rol=rol)
    return u


class _OnlyJefeView(JefeRequiredMixin, View):
    def get(self, request):
        from django.http import HttpResponse
        return HttpResponse("ok")


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


class MixinAccessTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _req(self, user):
        req = self.factory.get("/x/")
        req.user = user
        return _OnlyJefeView.as_view()(req)

    def test_wrong_role_gets_403(self):
        u = User.objects.create_user("enc", password="x")
        PerfilUsuario.objects.create(user=u, rol=PerfilUsuario.ROL_ENCUESTADOR)
        with self.assertRaises(PermissionDenied):
            self._req(u)

    def test_user_without_perfil_gets_403(self):
        u = User.objects.create_user("sinperfil", password="x")
        with self.assertRaises(PermissionDenied):
            self._req(u)

    def test_anonymous_redirects_to_login(self):
        resp = self._req(AnonymousUser())
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])
