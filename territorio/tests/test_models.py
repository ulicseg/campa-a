from django.test import TestCase
from territorio.models import Parcela

class ParcelaModelTest(TestCase):
    def test_svg_points_groups_into_xy_pairs(self):
        p = Parcela(numero=1, coords="265,366,332,324,370,386")
        self.assertEqual(p.svg_points, "265,366 332,324 370,386")

    def test_numero_is_unique(self):
        Parcela.objects.create(numero=1, coords="1,2,3,4")
        with self.assertRaises(Exception):
            Parcela.objects.create(numero=1, coords="5,6,7,8")
