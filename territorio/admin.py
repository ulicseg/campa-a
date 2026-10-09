from django.contrib import admin

from territorio.models import Barrio, Parcela


@admin.register(Barrio)
class BarrioAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ("numero", "barrio")
    list_filter = ("barrio",)
    search_fields = ("numero",)
    ordering = ("numero",)
