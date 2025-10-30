from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", include("apps.core.urls", namespace="core")),
        path("", include("apps.accounts.urls", namespace="accounts")),
        path("", include("apps.dashboard.urls", namespace="dashboard")),
        path("", include("apps.creators.urls", namespace="creators")),
        path("", include("apps.payments.urls", namespace="payments")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
