from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import JsonResponse
from django.urls import include, path

from root.sitemaps import sitemaps

urlpatterns = (
    [
        path(
            "admin/",
            include("admin_honeypot.urls", namespace="admin_honeypot"),
        ),
        path("dashboardx/", admin.site.urls),
        path("admin/defender/", include("defender.urls")),
        path("", include("apps.core.urls", namespace="core")),
        path("", include("apps.accounts.urls", namespace="accounts")),
        path("", include("apps.creators.urls", namespace="creators")),
        path("", include("apps.payments.urls", namespace="payments")),
        path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
        path("newsletter/", include("apps.newsletter.urls", namespace="newsletter")),
        path(
            "sitemap.xml",
            sitemap,
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
        path(
            "health/",
            lambda request: JsonResponse({"status": "healthy"}, status=200),
            name="health",
        ),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

handler400 = "django.views.defaults.bad_request"
handler403 = "django.views.defaults.permission_denied"
handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"
