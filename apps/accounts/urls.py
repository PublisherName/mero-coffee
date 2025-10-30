from django.urls import path

from apps.accounts.views import login, signup

app_name = "accounts"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login, name="login"),
]
