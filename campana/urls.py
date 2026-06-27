"""
URL configuration for campana project.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("usuarios/", include("usuarios.urls")),
    path("territorio/", include("territorio.urls")),
    path("encuestas/", include("encuestas.urls")),
    path("", include("dashboard.urls")),
]
