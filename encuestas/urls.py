from django.urls import path
from django.views.generic import TemplateView

from encuestas import views

urlpatterns = [
    path("cargar/", views.CargarFamilia.as_view(), name="cargar_familia"),
    # Placeholder — Task 8 will replace this with the real mis_cargas view.
    path("mias/", TemplateView.as_view(template_name="base.html"), name="mis_cargas"),
]
