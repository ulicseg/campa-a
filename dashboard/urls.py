from django.urls import path
from dashboard import views

urlpatterns = [
    path("", views.Dashboard.as_view(), name="dashboard"),
    path("aceptar-advertencia/", views.AceptarAdvertencia.as_view(), name="aceptar_advertencia"),
    path("parcela/<int:numero>/detalle/", views.DetalleParcela.as_view(), name="detalle_parcela"),
    path("parcela/<int:numero>/pdf/", views.PdfParcela.as_view(), name="pdf_parcela"),
    path("barrio/<int:pk>/pdf/", views.PdfBarrio.as_view(), name="pdf_barrio"),
]
