from django.urls import path

from apps.creators.views import creators_list, profile

app_name = "creators"

# Also has a creators url in apps.dashboard.urls
urlpatterns = [
    path("profile/<str:username>/", profile, name="profile"),
    path("creators/", creators_list, name="creators_list"),
]
