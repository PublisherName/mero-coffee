from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.forms import KYCForm
from apps.accounts.models import KYC

User = get_user_model()


def get_kyc_context(user):
    """Helper function to get KYC status for dashboard views."""
    if user.role == User.Roles.CREATOR:
        kyc, _ = KYC.objects.get_or_create(user=user)
        return {
            "kyc_status": kyc.status,
            "kyc": kyc,
        }
    return {}


@login_required
@role_required(User.Roles.CREATOR)
def dashboard(request):
    context = get_kyc_context(request.user)
    return render(request, "overview.html", context)


@login_required
@role_required(User.Roles.CREATOR)
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
    context.update(get_kyc_context(request.user))

    return render(request, "earnings.html", context)


@login_required
@role_required(User.Roles.CREATOR)
def withdrawal(request):
    available_balance = 5500

    # Payment method choices for the select component
    payment_method_choices = [
        ("bank", "Bank Transfer"),
        ("eSewa", "eSewa"),
        ("khalti", "Khalti"),
    ]

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
        "payment_method_choices": payment_method_choices,
        "withdrawals": withdrawals,
    }
    context.update(get_kyc_context(request.user))

    return render(request, "withdrawal.html", context)


@login_required
@role_required(User.Roles.CREATOR)
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
    context.update(get_kyc_context(request.user))

    return render(request, "supporters.html", context)


@login_required
@role_required(User.Roles.CREATOR)
def kyc(request):
    kyc, _ = KYC.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if kyc.status not in [KYC.Status.NOT_FILED, KYC.Status.REJECTED]:
            messages.error(request, "Your KYC is already submitted and cannot be modified.")
            return redirect("dashboard:kyc")

        form = KYCForm(request.POST, request.FILES, instance=kyc)
        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.status = KYC.Status.PENDING
            kyc.save()
            messages.success(request, "KYC submitted successfully. Awaiting admin approval.")
            return redirect("dashboard:kyc")
    else:
        form = KYCForm(instance=kyc)

    context = {
        "form": form,
        "kyc": kyc,
        "kyc_status": kyc.status if kyc.id else None,
    }
    return render(request, "kyc.html", context)
