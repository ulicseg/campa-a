from django.urls import path

from usuarios.views import GestionEncuestadores

urlpatterns = [
    path("encuestadores/", GestionEncuestadores.as_view(), name="gestion_encuestadores"),
]
