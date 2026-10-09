from django.urls import path

from territorio.views import BorrarBarrio, EditarBarrio, ListaBarrios

urlpatterns = [
    path("barrios/", ListaBarrios.as_view(), name="lista_barrios"),
    path("barrios/<int:pk>/", EditarBarrio.as_view(), name="editar_barrio"),
    path("barrios/<int:pk>/borrar/", BorrarBarrio.as_view(), name="borrar_barrio"),
]
