from django.urls import path
from dashboard import views

urlpatterns = [
    path("", views.Dashboard.as_view(), name="dashboard"),
    path("aceptar-advertencia/", views.AceptarAdvertencia.as_view(), name="aceptar_advertencia"),
    path("parcela/<int:numero>/detalle/", views.DetalleParcela.as_view(), name="detalle_parcela"),
]
