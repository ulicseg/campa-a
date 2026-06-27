"""
URL configuration for campana project.
"""
from django.contrib import admin
from django.urls import include, path
from usuarios.views import PostLoginRedirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", PostLoginRedirect.as_view(), name="home"),
    path("encuestas/", include("encuestas.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("territorio/", include("territorio.urls")),
    path("usuarios/", include("usuarios.urls")),
]
