from django.urls import path

from apps.creators.views import creators_list, profile

app_name = "creators"

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("creators/", creators_list, name="creators_list"),
]
