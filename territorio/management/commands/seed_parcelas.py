import re
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from territorio.models import Parcela

AREA_RE = re.compile(r'alt="(\d+)"[^>]*coords="([\d,-]+)"')


class Command(BaseCommand):
    help = "Carga las parcelas desde coordenadas.md (idempotente)."

    def handle(self, *args, **options):
        path = Path(settings.BASE_DIR) / "coordenadas.md"
        text = path.read_text(encoding="utf-8")
        count = 0
        for numero, coords in AREA_RE.findall(text):
            Parcela.objects.update_or_create(
                numero=int(numero), defaults={"coords": coords}
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"{count} parcelas cargadas."))
