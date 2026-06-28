from django import forms
from territorio.models import Parcela


class EncuestadorForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nombre de usuario")
    password = forms.CharField(
        widget=forms.PasswordInput, min_length=8, label="Contraseña inicial"
    )
    parcelas = forms.ModelMultipleChoiceField(
        queryset=Parcela.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Parcelas asignadas",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Render each parcela choice as just its number, so the field can be
        # shown as a compact grid of numbered chips instead of a long checkbox list.
        self.fields["parcelas"].label_from_instance = lambda parcela: str(parcela.numero)
