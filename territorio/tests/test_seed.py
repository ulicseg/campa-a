from django.test import TestCase
from django.core.management import call_command
from territorio.models import Parcela


class SeedParcelasTest(TestCase):
    def test_seed_creates_64_parcelas(self):
        call_command("seed_parcelas")
        self.assertEqual(Parcela.objects.count(), 64)
        self.assertTrue(Parcela.objects.filter(numero=1).exists())
        self.assertTrue(Parcela.objects.filter(numero=64).exists())

    def test_seed_is_idempotent(self):
        call_command("seed_parcelas")
        call_command("seed_parcelas")
        self.assertEqual(Parcela.objects.count(), 64)
