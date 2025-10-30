from django.shortcuts import render


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
            "description": "Get paid instantly through eSewa or Khalti",
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
        "core/homepage.html",
        {
            "features": features,
            "how_it_works": how_it_works,
            "featured_creators": featured_creators,
            "pricing_comparison": pricing_comparison,
        },
    )


def how_it_works(request):
    return render(request, "core/how_it_works.html", {})


def pricing(request):
    return render(request, "core/pricing.html", {})
