from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist, loader


def homepage(request):
    # Dummy data for demonstration
    features = [
        {
            "icon": "⚡",
            "title": "Simple Setup",
            "description": "Create your page in minutes with our easy-to-use interface",
        },
        {
            "icon": "💳",
            "title": "Local Payments",
            "description": "Accept payments through eSewa and Khalti",
        },
        {
            "icon": "💰",
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

    featured_creators = [
        {
            "name": "Aashish Shrestha",
            "category": "Digital Artist",
            "supporters": 234,
            "monthly": "Rs. 15,600",
            "avatar_color": "#FF6B6B",
        },
        {
            "name": "Samjhana Tamang",
            "category": "Music Creator",
            "supporters": 156,
            "monthly": "Rs. 8,900",
            "avatar_color": "#4ECDC4",
        },
        {
            "name": "Rohan KC",
            "category": "Tech Educator",
            "supporters": 89,
            "monthly": "Rs. 6,200",
            "avatar_color": "#95E1D3",
        },
        {
            "name": "Priya Maharjan",
            "category": "Writer",
            "supporters": 67,
            "monthly": "Rs. 4,800",
            "avatar_color": "#F38181",
        },
    ]

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
