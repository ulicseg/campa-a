from django.contrib.auth.models import User
from django.test import TestCase

from territorio.models import Barrio, Parcela
from usuarios.models import PerfilUsuario


class BarriosTest(TestCase):
    def setUp(self):
        self.p1 = Parcela.objects.create(numero=1, coords="1,2,3,4")
        self.p2 = Parcela.objects.create(numero=2, coords="1,2,3,4")
        self.p3 = Parcela.objects.create(numero=3, coords="1,2,3,4")
        jefe = User.objects.create_user("jefe", password="x")
        PerfilUsuario.objects.create(user=jefe, rol="jefe")
        self.client.login(username="jefe", password="x")

    def test_encuestador_gets_403(self):
        u = User.objects.create_user("ana", password="x")
        PerfilUsuario.objects.create(user=u, rol="encuestador")
        self.client.login(username="ana", password="x")
        self.assertEqual(self.client.get("/territorio/barrios/").status_code, 403)

    def test_jefe_ve_lista(self):
        Barrio.objects.create(nombre="Prueba")
        resp = self.client.get("/territorio/barrios/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Prueba")

    def test_crear_barrio(self):
        resp = self.client.post("/territorio/barrios/", {"nombre": "Prueba"})
        barrio = Barrio.objects.get(nombre="Prueba")
        self.assertRedirects(resp, f"/territorio/barrios/{barrio.pk}/")

    def test_nombre_duplicado_no_se_crea(self):
        Barrio.objects.create(nombre="Prueba")
        resp = self.client.post("/territorio/barrios/", {"nombre": "Prueba"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Barrio.objects.filter(nombre="Prueba").count(), 1)

    def test_editar_muestra_barrio_de_otra_manzana(self):
        norte = Barrio.objects.create(nombre="Prueba Norte")
        sur = Barrio.objects.create(nombre="Prueba Sur")
        Parcela.objects.filter(pk=self.p1.pk).update(barrio=norte)
        resp = self.client.get(f"/territorio/barrios/{sur.pk}/")
        self.assertContains(resp, "hoy en Prueba Norte")

    def test_asignar_manzanas(self):
        barrio = Barrio.objects.create(nombre="Prueba")
        self.client.post(f"/territorio/barrios/{barrio.pk}/", {"parcelas": [self.p1.pk, self.p2.pk]})
        self.assertEqual(set(barrio.parcelas.all()), {self.p1, self.p2})

    def test_desmarcar_quita_manzana(self):
        barrio = Barrio.objects.create(nombre="Prueba")
        Parcela.objects.filter(pk__in=[self.p1.pk, self.p2.pk]).update(barrio=barrio)
        self.client.post(f"/territorio/barrios/{barrio.pk}/", {"parcelas": [self.p1.pk]})
        self.p2.refresh_from_db()
        self.assertIsNone(self.p2.barrio)
        self.assertEqual(list(barrio.parcelas.all()), [self.p1])

    def test_manzana_de_otro_barrio_se_mueve(self):
        norte = Barrio.objects.create(nombre="Prueba Norte")
        sur = Barrio.objects.create(nombre="Prueba Sur")
        Parcela.objects.filter(pk=self.p3.pk).update(barrio=norte)
        self.client.post(f"/territorio/barrios/{sur.pk}/", {"parcelas": [self.p3.pk]})
        self.p3.refresh_from_db()
        self.assertEqual(self.p3.barrio, sur)

    def test_borrar_barrio_libera_manzanas(self):
        barrio = Barrio.objects.create(nombre="Prueba")
        Parcela.objects.filter(pk=self.p1.pk).update(barrio=barrio)
        self.client.post(f"/territorio/barrios/{barrio.pk}/borrar/")
        self.assertFalse(Barrio.objects.filter(pk=barrio.pk).exists())
        self.p1.refresh_from_db()
        self.assertIsNone(self.p1.barrio)

    def test_barrios_iniciales_cargados(self):
        self.assertEqual(Barrio.objects.count(), 26)
        self.assertTrue(Barrio.objects.filter(nombre="Néstor Kirchner (25 VIVIENDAS)").exists())
