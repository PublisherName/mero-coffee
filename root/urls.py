from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", include("apps.core.urls", namespace="core")),
        path("", include("apps.accounts.urls", namespace="accounts")),
        path("", include("apps.creators.urls", namespace="creators")),
        path("", include("apps.payments.urls", namespace="payments")),
        path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

handler400 = "django.views.defaults.bad_request"
handler403 = "django.views.defaults.permission_denied"
handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"
