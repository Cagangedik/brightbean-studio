from django.urls import path

from apps.legal import views

app_name = "legal"

urlpatterns = [
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
]
