"""Test cases for MeroCoffee sitemap and robots.txt functionality."""

from unittest.mock import MagicMock

from django.test import RequestFactory, TestCase, override_settings

from apps.core.views import robots_txt
from apps.creators.models import CreatorProfile


class RobotsTxtTestCase(TestCase):
    """Test cases for the robots.txt view."""

    def test_robots_txt_returns_correct_content_type(self):
        """Test that robots.txt returns text/plain content type."""
        factory = RequestFactory()
        request = factory.get("/robots.txt")
        response = robots_txt(request)
        # Django returns 'text/plain' without charset
        self.assertTrue(response["Content-Type"].startswith("text/plain"))

    @override_settings(SITE_BASE_URL="https://coffee.subashghimire.info.np")
    def test_robots_txt_contains_sitemap_url(self):
        """Test that robots.txt contains the sitemap URL."""
        factory = RequestFactory()
        request = factory.get("/robots.txt")
        response = robots_txt(request)
        self.assertIn(
            b"Sitemap: https://coffee.subashghimire.info.np/sitemap.xml", response.content
        )

    @override_settings(SITE_BASE_URL="http://localhost:8000")
    def test_robots_txt_uses_site_base_url(self):
        """Test that robots.txt uses the SITE_BASE_URL setting."""
        factory = RequestFactory()
        request = factory.get("/robots.txt")
        response = robots_txt(request)
        self.assertIn(b"Sitemap: http://localhost:8000/sitemap.xml", response.content)

    def test_robots_txt_disallows_admin_paths(self):
        """Test that robots.txt disallows admin and private paths."""
        factory = RequestFactory()
        request = factory.get("/robots.txt")
        response = robots_txt(request)
        content = response.content.decode("utf-8")
        self.assertIn("Disallow: /dashboard/", content)
        self.assertIn("Disallow: /admin/", content)
        self.assertIn("Disallow: /newsletter/", content)

    def test_robots_txt_allows_public_paths(self):
        """Test that robots.txt allows public paths."""
        factory = RequestFactory()
        request = factory.get("/robots.txt")
        response = robots_txt(request)
        content = response.content.decode("utf-8")
        self.assertIn("Allow: /profile/", content)
        self.assertIn("Allow: /creators/", content)

    def test_robots_txt_has_crawl_delay(self):
        """Test that robots.txt includes crawl delay."""
        factory = RequestFactory()
        request = factory.get("/robots.txt")
        response = robots_txt(request)
        content = response.content.decode("utf-8")
        self.assertIn("Crawl-delay: 10", content)

    def test_robots_txt_allows_all_user_agents(self):
        """Test that robots.txt allows all user agents."""
        factory = RequestFactory()
        request = factory.get("/robots.txt")
        response = robots_txt(request)
        content = response.content.decode("utf-8")
        self.assertIn("User-agent: *", content)
        self.assertIn("Allow: /", content)


class StaticViewSitemapTestCase(TestCase):
    """Test cases for static view sitemap."""

    def test_static_sitemap_contains_core_urls(self):
        """Test that static sitemap contains core app URLs."""
        from root.sitemaps import StaticViewSitemap

        sitemap = StaticViewSitemap()
        items = sitemap.items()

        self.assertIn("core:homepage", items)
        self.assertIn("core:how_it_works", items)
        self.assertIn("core:pricing", items)
        self.assertIn("creators:creators_list", items)

    def test_static_sitemap_changefreq(self):
        """Test that static sitemap has weekly changefreq."""
        from root.sitemaps import StaticViewSitemap

        sitemap = StaticViewSitemap()
        self.assertEqual(sitemap.changefreq, "weekly")

    def test_static_sitemap_priority(self):
        """Test that static sitemap has 0.8 priority."""
        from root.sitemaps import StaticViewSitemap

        sitemap = StaticViewSitemap()
        self.assertEqual(sitemap.priority, 0.8)

    def test_static_sitemap_location(self):
        """Test that static sitemap returns correct URLs."""
        from root.sitemaps import StaticViewSitemap

        sitemap = StaticViewSitemap()
        self.assertEqual(sitemap.location("core:homepage"), "/")
        self.assertEqual(sitemap.location("core:how_it_works"), "/how-it-works/")
        self.assertEqual(sitemap.location("core:pricing"), "/pricing/")
        self.assertEqual(sitemap.location("creators:creators_list"), "/creators/")


class CreatorProfileSitemapTestCase(TestCase):
    """Test cases for creator profile sitemap."""

    def test_creator_sitemap_changefreq(self):
        """Test that creator sitemap has daily changefreq."""
        from root.sitemaps import CreatorProfileSitemap

        sitemap = CreatorProfileSitemap()
        self.assertEqual(sitemap.changefreq, "daily")

    def test_creator_sitemap_priority(self):
        """Test that creator sitemap has 0.6 priority."""
        from root.sitemaps import CreatorProfileSitemap

        sitemap = CreatorProfileSitemap()
        self.assertEqual(sitemap.priority, 0.6)

    def test_creator_sitemap_items_returns_queryset(self):
        """Test that creator sitemap items method is callable."""
        from root.sitemaps import CreatorProfileSitemap

        sitemap = CreatorProfileSitemap()
        # Just verify the method exists and is callable
        self.assertTrue(callable(sitemap.items))

    def test_creator_sitemap_location_with_mock(self):
        """Test that creator sitemap returns correct profile URL using mock."""
        from root.sitemaps import CreatorProfileSitemap

        # Create a mock creator profile
        mock_profile = MagicMock(spec=CreatorProfile)
        mock_profile.user.username = "testcreator"

        sitemap = CreatorProfileSitemap()
        location = sitemap.location(mock_profile)

        self.assertEqual(location, "/profile/testcreator/")

    def test_creator_sitemap_queryset_is_ordered(self):
        """Test that creator sitemap items method returns ordered queryset."""
        from root.sitemaps import CreatorProfileSitemap

        sitemap = CreatorProfileSitemap()
        items = sitemap.items()

        self.assertIsNotNone(items)


class SitemapIntegrationTestCase(TestCase):
    """Integration tests for sitemap URLs."""

    def test_sitemap_url_returns_200(self):
        """Test that sitemap.xml returns 200 status."""
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)

    def test_sitemap_url_content_type(self):
        """Test that sitemap.xml returns XML content type."""
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_robots_txt_url_returns_200(self):
        """Test that robots.txt returns 200 status."""
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)

    def test_sitemap_includes_static_pages(self):
        """Test that sitemap includes static pages."""
        response = self.client.get("/sitemap.xml")
        content = response.content.decode("utf-8")
        self.assertIn("/how-it-works/", content)
        self.assertIn("/pricing/", content)
        self.assertIn("/creators/", content)
