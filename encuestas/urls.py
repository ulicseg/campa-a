from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        "cargar/",
        TemplateView.as_view(template_name="base.html"),
        name="cargar_familia",
    ),
]
