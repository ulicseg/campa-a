from django.db import models


class Barrio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Parcela(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    coords = models.TextField(help_text="Pares x,y separados por coma, del image map.")
    # Cada manzana pertenece a lo sumo a un barrio.
    barrio = models.ForeignKey(
        Barrio, null=True, blank=True, on_delete=models.SET_NULL, related_name="parcelas"
    )

    class Meta:
        ordering = ["numero"]

    def __str__(self):
        return f"Cuadra {self.numero}"

    @property
    def svg_points(self):
        nums = self.coords.split(",")
        pairs = [f"{nums[i]},{nums[i+1]}" for i in range(0, len(nums) - 1, 2)]
        return " ".join(pairs)
