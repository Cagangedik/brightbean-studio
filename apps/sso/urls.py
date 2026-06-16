from django.urls import path

from apps.sso import views

app_name = "sso"

urlpatterns = [
    path("launch", views.launch, name="launch"),
]
