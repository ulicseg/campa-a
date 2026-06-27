from django.urls import path
from dashboard import views

urlpatterns = [
    path("", views.Dashboard.as_view(), name="dashboard"),
]
