from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist, loader

from apps.creators.models import CreatorProfile


def homepage(request):
    features = [
        {
            "title": "Simple Setup",
            "description": "Create your page in minutes with our easy-to-use interface",
        },
        {
            "title": "Local Payments",
            "description": "Accept payments through eSewa and Khalti",
        },
        {
            "title": "Keep More",
            "description": "First Rs. 5,000/month free, then only 3-5% fee",
        },
    ]

    how_it_works = [
        {
            "step": 1,
            "title": "Create Your Page",
            "description": "Set up your profile, bio, and coffee price in just 5 minutes",
        },
        {
            "step": 2,
            "title": "Share Your Link",
            "description": "Share your unique page with your audience on social media",
        },
        {
            "step": 3,
            "title": "Receive Support",
            "description": "Start receiving support from your fans instantly via eSewa or Khalti",
        },
    ]

    creators_qs = CreatorProfile.objects.active_creators_with_stats().select_related("user")[:4]
    featured_creators = []
    for c in creators_qs:
        name = c.display_name or c.user.get_full_name() or c.user.username
        monthly = c.monthly_income or 0
        featured_creators.append(
            {
                "name": name,
                "username": c.user.username,
                "supporters": c.supporter_count,
                "monthly": f"Rs. {monthly:,}",
                "avatar_color": c.avatar_color,
            }
        )

    pricing_comparison = {
        "nepal_platform": {
            "name": "MeroCoffee",
            "fee_structure": "Free up to Rs. 5,000/month, then 3-5%",
            "payment_methods": "eSewa, Khalti",
            "currency": "NPR",
            "withdrawal": "Direct to Nepal bank account",
        },
        "buy_me_coffee": {
            "name": "Buy Me a Coffee",
            "fee_structure": "Flat 5%",
            "payment_methods": "Stripe, PayPal (USD only)",
            "currency": "USD (conversion fees apply)",
            "withdrawal": "International wire transfer",
        },
    }

    return render(
        request,
        "homepage.html",
        {
            "features": features,
            "how_it_works": how_it_works,
            "featured_creators": featured_creators,
            "pricing_comparison": pricing_comparison,
        },
    )


def how_it_works(request):
    return render(request, "how_it_works.html", {})


def pricing(request):
    return render(request, "pricing.html", {})


def ratelimit_lockout_view(request, exception=None):
    return render(request, "ratelimit_lockout.html", status=429)


def robots_txt(request):
    """Serve robots.txt file for SEO purposes."""
    sitemap_url = f"{settings.SITE_BASE_URL.rstrip('/')}/sitemap.xml"
    try:
        template = loader.get_template("robots.txt")
        content = template.render({"sitemap_url": sitemap_url})
        return HttpResponse(content, content_type="text/plain")
    except TemplateDoesNotExist:
        default_robots = f"""User-agent: *
Allow: /

Sitemap: {sitemap_url}

Disallow: /dashboard/
Disallow: /admin/
Disallow: /newsletter/
"""
        return HttpResponse(default_robots, content_type="text/plain")
