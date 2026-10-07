from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from territorio.models import Parcela
from usuarios.models import PerfilUsuario


class Command(BaseCommand):
    help = (
        "Crea (o actualiza) una cuenta de encuestador por parcela: "
        "usuario y contraseña 'parcelaX', asignada a la parcela X (idempotente)."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        parcelas = list(Parcela.objects.all())
        if not parcelas:
            self.stderr.write(
                self.style.ERROR("No hay parcelas. Ejecutá primero: seed_parcelas")
            )
            return
        creadas = actualizadas = 0
        for parcela in parcelas:
            username = f"parcela{parcela.numero}"
            user, creada = User.objects.get_or_create(username=username)
            user.set_password(username)
            user.save()
            perfil, _ = PerfilUsuario.objects.update_or_create(
                user=user, defaults={"rol": PerfilUsuario.ROL_ENCUESTADOR}
            )
            perfil.parcelas.set([parcela])
            if creada:
                creadas += 1
            else:
                actualizadas += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"{creadas} cuentas creadas, {actualizadas} actualizadas."
            )
        )
