# encuestas/models.py
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from territorio.models import Parcela


class Familia(models.Model):
    numero_familia = models.CharField(max_length=20)
    nombre_familia = models.CharField(max_length=120)
    integrantes = models.PositiveIntegerField(default=1)
    contacto_1 = models.CharField(max_length=60, blank=True)
    contacto_2 = models.CharField(max_length=60, blank=True)
    parcela = models.ForeignKey(Parcela, on_delete=models.PROTECT, related_name="familias")
    cargada_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name="familias_cargadas")
    fecha = models.DateTimeField(auto_now_add=True)
    consentimiento_informado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre_familia} (cuadra {self.parcela.numero})"


class Voto(models.Model):
    INTENCIONES = [("PJ", "PJ"), ("UCR", "UCR"), ("Otro", "Otro"),
                   ("Indeciso", "Indeciso"), ("No contesta", "No contesta")]
    familia = models.OneToOneField(Familia, on_delete=models.CASCADE, related_name="voto")
    intencion = models.CharField(max_length=20, choices=INTENCIONES)

    def clean(self):
        valid = {c for c, _ in self.INTENCIONES}
        if self.intencion not in valid:
            raise ValidationError({"intencion": "Intención inválida."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
