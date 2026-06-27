# encuestas/forms.py
from django import forms
from encuestas.models import Voto
from territorio.models import Parcela

CONSENT_LABEL = (
    "Confirmo que el vecino fue informado de que estos datos "
    "son para uso estadístico y de campaña"
)


class FamiliaForm(forms.Form):
    numero_familia = forms.CharField(max_length=20)
    nombre_familia = forms.CharField(max_length=120)
    integrantes = forms.IntegerField(min_value=1)
    contacto_1 = forms.CharField(max_length=60, required=False)
    contacto_2 = forms.CharField(max_length=60, required=False)
    parcela = forms.ModelChoiceField(queryset=None)
    intencion = forms.ChoiceField(choices=Voto.INTENCIONES)
    consentimiento_informado = forms.BooleanField(label=CONSENT_LABEL)  # required=True by default

    def __init__(self, *args, parcelas_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parcela"].queryset = parcelas_qs
