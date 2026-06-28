from django.contrib import admin

from usuarios.models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "rol")
    list_filter = ("rol",)
    search_fields = ("user__username",)
    filter_horizontal = ("parcelas",)
