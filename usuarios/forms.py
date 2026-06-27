from django import forms
from territorio.models import Parcela


class EncuestadorForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    parcelas = forms.ModelMultipleChoiceField(
        queryset=Parcela.objects.all(), widget=forms.CheckboxSelectMultiple)
