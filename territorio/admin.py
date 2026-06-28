from django.contrib import admin

from territorio.models import Parcela


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ("numero",)
    search_fields = ("numero",)
    ordering = ("numero",)
