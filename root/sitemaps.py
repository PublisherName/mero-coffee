"""
Sitemap configuration for MeroCoffee SEO.

This module defines sitemaps for both static pages and dynamic creator profiles
to improve search engine indexing and SEO performance.
"""

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.creators.models import CreatorProfile


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages like homepage, how-it-works, pricing, etc."""

    changefreq = "weekly"
    priority = 0.8

    def items(self):  # noqa: PLR6301
        return [
            "core:homepage",
            "core:how_it_works",
            "core:pricing",
            "creators:creators_list",
        ]

    def location(self, obj):  # noqa: PLR6301
        return reverse(obj)

    def lastmod(self, obj):  # noqa: PLR6301
        """Return None as static pages don't have modification dates."""
        return


class CreatorProfileSitemap(Sitemap):
    """Sitemap for individual creator profile pages."""

    changefreq = "daily"
    priority = 0.6

    def items(self):  # noqa: PLR6301
        """Return active creator profiles for sitemap inclusion."""
        return CreatorProfile.objects.filter(is_active=True).select_related("user").order_by("id")

    def location(self, obj):  # noqa: PLR6301
        """Generate URL for creator profile using username."""
        return reverse("creators:profile", kwargs={"username": obj.user.username})

    def lastmod(self, obj):  # noqa: PLR6301
        """Use profile's last modification time."""
        return getattr(obj, "updated_at", None)

    def get_urls(self, site=None, **kwargs):
        """Override to add https protocol for secure environments."""
        urls = super().get_urls(site=site, **kwargs)
        for url in urls:
            # Force HTTPS in production/staging environments
            if settings.IS_SERVER_SECURE:
                url["protocol"] = "https"
        return urls


# Sitemap configuration for Django's sitemap framework
sitemaps = {
    "static": StaticViewSitemap,
    "creators": CreatorProfileSitemap,
}

# Cache timeout for sitemap in seconds (1 hour)
SITEMAP_CACHE_TIMEOUT = 3600
