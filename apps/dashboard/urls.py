from django.urls import path

from apps.dashboard.views import dashboard, earnings, page_settings, supporters, withdrawal

app_name = "dashboard"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("page-settings/", page_settings, name="page_settings"),
    path("earnings/", earnings, name="earnings"),
    path("withdrawal/", withdrawal, name="withdrawal"),
    path("supporters/", supporters, name="supporters"),
]
