from django import forms

from territorio.models import Barrio, Parcela


class BarrioForm(forms.ModelForm):
    class Meta:
        model = Barrio
        fields = ["nombre"]
        labels = {"nombre": "Nombre del barrio"}


class AsignarParcelasForm(forms.Form):
    parcelas = forms.ModelMultipleChoiceField(
        queryset=Parcela.objects.select_related("barrio"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Manzanas del barrio",
    )

    def __init__(self, *args, barrio, **kwargs):
        super().__init__(*args, **kwargs)
        self.barrio = barrio
        self.fields["parcelas"].label_from_instance = lambda parcela: str(parcela.numero)
        if not self.is_bound:
            self.initial["parcelas"] = list(barrio.parcelas.values_list("pk", flat=True))

    def save(self):
        """Deja en el barrio exactamente las manzanas elegidas.

        Una manzana elegida que estaba en otro barrio se mueve a este.
        """
        elegidas = self.cleaned_data["parcelas"]
        self.barrio.parcelas.exclude(pk__in=elegidas).update(barrio=None)
        Parcela.objects.filter(pk__in=elegidas).update(barrio=self.barrio)
