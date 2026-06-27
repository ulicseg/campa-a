from django.urls import path

from encuestas import views

urlpatterns = [
    path("cargar/", views.CargarFamilia.as_view(), name="cargar_familia"),
    path("mias/", views.MisCargas.as_view(), name="mis_cargas"),
    path("<int:pk>/editar/", views.EditarFamilia.as_view(), name="editar_familia"),
    path("<int:pk>/borrar/", views.BorrarFamilia.as_view(), name="borrar_familia"),
]
