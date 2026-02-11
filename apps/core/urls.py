from django.urls import path

from apps.core.views import (
    homepage,
    how_it_works,
    pricing,
    robots_txt,
)

app_name = "core"

urlpatterns = [
    path("", homepage, name="homepage"),
    path("how-it-works/", how_it_works, name="how_it_works"),
    path("pricing/", pricing, name="pricing"),
    path("robots.txt", robots_txt, name="robots_txt"),
]
