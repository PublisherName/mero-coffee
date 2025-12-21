from django.urls import path

from . import views

app_name = "newsletter"

urlpatterns = [
    path("subscribe/", views.subscribe, name="subscribe"),
    path("verify/<uuid:token>/", views.verify_email, name="verify_email"),
]
