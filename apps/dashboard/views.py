from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.forms import KYCForm
from apps.accounts.models import KYC
from apps.creators.models import CreatorProfile
from apps.payments.forms import WithdrawalForm
from apps.payments.models import SupportTransaction, Withdrawal

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
    creator_profile = CreatorProfile.objects.get(user=request.user)

    completed_transactions = SupportTransaction.objects.filter(
        creator=creator_profile, payment_status=SupportTransaction.Status.COMPLETED
    )

    recent_supporters = completed_transactions.order_by("-created_at")[:5]

    # Calculate stats
    total_earnings = completed_transactions.aggregate(total=models.Sum("amount"))["total"] or 0

    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_earnings = (
        completed_transactions.filter(
            created_at__year=current_year, created_at__month=current_month
        ).aggregate(total=models.Sum("amount"))["total"]
        or 0
    )

    supporter_count = completed_transactions.count()

    average_support = total_earnings / supporter_count if supporter_count > 0 else 0

    context = {
        "recent_supporters": recent_supporters,
        "total_earnings": total_earnings,
        "monthly_earnings": monthly_earnings,
        "supporter_count": supporter_count,
        "average_support": round(average_support, 2),
    }
    context.update(get_kyc_context(request.user))
    return render(request, "overview.html", context)


@login_required
@role_required(User.Roles.CREATOR)
def earnings(request):
    creator_profile = CreatorProfile.objects.get(user=request.user)

    completed_transactions = SupportTransaction.objects.filter(
        creator=creator_profile, payment_status=SupportTransaction.Status.COMPLETED
    )

    total_earnings = completed_transactions.aggregate(total=models.Sum("amount"))["total"] or 0

    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_earnings = (
        completed_transactions.filter(
            created_at__year=current_year, created_at__month=current_month
        ).aggregate(total=models.Sum("amount"))["total"]
        or 0
    )

    processed_withdrawals = (
        Withdrawal.objects.filter(
            creator=creator_profile, status=Withdrawal.Status.PROCESSED
        ).aggregate(total=models.Sum("amount"))["total"]
        or 0
    )

    pending_payout = total_earnings - processed_withdrawals

    earnings_list = completed_transactions.order_by("-created_at").values(
        "created_at", "supporter_name", "amount", "message"
    )

    # Calculate monthly earnings for chart (last 6 months)
    chart_labels = []
    chart_data = []
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30 * i)
        month = month_date.month
        year = month_date.year
        monthly_sum = (
            completed_transactions.filter(
                created_at__year=year, created_at__month=month
            ).aggregate(total=models.Sum("amount"))["total"]
            or 0
        )
        chart_labels.append(month_date.strftime("%B %Y"))
        chart_data.append(monthly_sum)

    context = {
        "total_earnings": total_earnings,
        "monthly_earnings": monthly_earnings,
        "pending_payout": pending_payout,
        "earnings_list": earnings_list,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
    }
    context.update(get_kyc_context(request.user))

    return render(request, "earnings.html", context)


@login_required
@role_required(User.Roles.CREATOR)
def withdrawal(request):
    creator_profile = CreatorProfile.objects.by_username(username=request.user.username).first()
    if request.method == "POST":
        form = WithdrawalForm(request.POST, creator_profile=creator_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Withdrawal request submitted successfully.")
            return redirect("dashboard:withdrawal")
    else:
        form = WithdrawalForm(creator_profile=creator_profile)

    withdrawals = creator_profile.withdrawals.order_by("-requested_at")[:10]

    context = {
        "form": form,
        "withdrawals": withdrawals,
        "available_balance": creator_profile.available_balance,
        "pending_balance": creator_profile.pending_balance,
        "withdrawn_balance": creator_profile.withdrawn_balance,
        "min_withdrawal": settings.MIN_WITHDRAWAL_AMOUNT,
    }
    context.update(get_kyc_context(request.user))

    return render(request, "withdrawal.html", context)


@login_required
@role_required(User.Roles.CREATOR)
def supporters(request):
    creator_profile = CreatorProfile.objects.get(user=request.user)
    recent_supporters = SupportTransaction.objects.filter(
        creator=creator_profile, payment_status=SupportTransaction.Status.COMPLETED
    ).order_by("-created_at")[:25]

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
