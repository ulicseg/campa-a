from django.urls import path
from dashboard import views

urlpatterns = [
    path("", views.Dashboard.as_view(), name="dashboard"),
    path("parcela/<int:numero>/detalle/", views.DetalleParcela.as_view(), name="detalle_parcela"),
]
