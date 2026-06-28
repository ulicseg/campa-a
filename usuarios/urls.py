from django.urls import path

from usuarios.views import BorrarEncuestador, GestionEncuestadores

urlpatterns = [
    path("encuestadores/", GestionEncuestadores.as_view(), name="gestion_encuestadores"),
    path(
        "encuestadores/<int:pk>/borrar/",
        BorrarEncuestador.as_view(),
        name="borrar_encuestador",
    ),
]
