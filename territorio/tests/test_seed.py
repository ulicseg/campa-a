from django.test import TestCase
from django.core.management import call_command
from territorio.models import Parcela


class SeedParcelasTest(TestCase):
    def test_seed_creates_all_parcelas(self):
        call_command("seed_parcelas")
        self.assertEqual(Parcela.objects.count(), 72)
        self.assertTrue(Parcela.objects.filter(numero=1).exists())
        self.assertTrue(Parcela.objects.filter(numero=72).exists())

    def test_seed_is_idempotent(self):
        call_command("seed_parcelas")
        call_command("seed_parcelas")
        self.assertEqual(Parcela.objects.count(), 72)
