from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    return render(request, "overview.html", {})


@login_required
def earnings(request):
    context = {
        "total_earnings": 12450,
        "monthly_earnings": 3200,
        "pending_payout": 1500,
        "supporter_count": 47,
        "earnings_list": [
            {
                "date": datetime(2025, 11, 28),
                "supporter_name": "Subash Ghimire",
                "amount": 500,
                "message": "Great content!",
            },
        ],
    }

    return render(request, "earnings.html", context)


@login_required
def withdrawal(request):
    available_balance = 5500

    # Dummy withdrawal history data
    withdrawals = [
        {
            "date": datetime.now() - timedelta(days=1),
            "amount": 1000,
            "payment_method": "eSewa",
            "status": "completed",
        },
        {
            "date": datetime.now() - timedelta(days=5),
            "amount": 1500,
            "payment_method": "Bank Transfer",
            "status": "pending",
        },
        {
            "date": datetime.now() - timedelta(days=10),
            "amount": 2000,
            "payment_method": "khalti",
            "status": "rejected",
        },
    ]

    context = {
        "available_balance": available_balance,
        "withdrawals": withdrawals,
    }
    return render(request, "withdrawal.html", context)


@login_required
def supporters(request):
    # Dummy supporters data
    recent_supporters = [
        {
            "name": "Bibek Ghimire",
            "amount": 500,
            "message": "Great content! Keep it up! 🔥",
            "date": datetime.now() - timedelta(hours=2),
        },
        {
            "name": "Sneha Poudel",
            "amount": 200,
            "message": "Love your work!",
            "date": datetime.now() - timedelta(hours=5),
        },
        {
            "name": "Rajesh Thapa",
            "amount": 100,
            "message": None,
            "date": datetime.now() - timedelta(days=1),
        },
    ]

    context = {
        "supporters": recent_supporters,
    }
    return render(request, "supporters.html", context)
