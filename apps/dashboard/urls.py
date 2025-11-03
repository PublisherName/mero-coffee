from django.urls import path

from apps.creators.views import profile_settings
from apps.dashboard.views import dashboard, earnings, supporters, withdrawal

app_name = "dashboard"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("profile-settings/", profile_settings, name="profile_settings"),
    path("earnings/", earnings, name="earnings"),
    path("withdrawal/", withdrawal, name="withdrawal"),
    path("supporters/", supporters, name="supporters"),
]
