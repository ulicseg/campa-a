from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from usuarios.models import PerfilUsuario


class Command(BaseCommand):
    help = "Crea (o actualiza) un Jefe de Campaña (rol de la app, sin permisos de Django admin)."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Nombre de usuario del jefe.")
        parser.add_argument(
            "--password", required=True, help="Contraseña del jefe."
        )

    def handle(self, *args, **options):
        username = options["username"]
        user, _ = User.objects.get_or_create(username=username)
        user.set_password(options["password"])
        user.save()
        PerfilUsuario.objects.update_or_create(
            user=user, defaults={"rol": PerfilUsuario.ROL_JEFE}
        )
        self.stdout.write(
            self.style.SUCCESS(f"Jefe de Campaña '{username}' listo.")
        )
