import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.dashboard.views import get_kyc_context
from apps.payments.models import PaymentGateway, SupportTransaction

from .forms import BuyCoffeeForm, CreatorProfileForm
from .models import CreatorProfile


def profile(request, username):
    creator = get_object_or_404(CreatorProfile.objects.by_username(username))
    supporter_count = creator.supporters
    monthly_income = 10000

    if request.method == "POST":
        form = BuyCoffeeForm(request.POST, coffee_price=creator.coffee_price)
        if form.is_valid():
            transaction = SupportTransaction.objects.create(
                creator=creator,
                supporter_name=form.cleaned_data["supporter_name"],
                amount=form.cleaned_data["amount"],
                payment_method=form.cleaned_data["payment_provider"],
                message=form.cleaned_data["message"],
                transaction_id=str(uuid.uuid4()),
                payment_status="pending",
            )
            return redirect("payments:checkout", transaction_id=transaction.transaction_id)
        messages.error(request, "Please correct the errors in the form.")
    else:
        form = BuyCoffeeForm(coffee_price=creator.coffee_price)

    context = {
        "creator": creator,
        "form": form,
        "supporter_count": supporter_count,
        "monthly_income": monthly_income,
        "payment_gateways": PaymentGateway.objects.filter(is_active=True),
        "amount_multiples": {
            "1x": creator.coffee_price,
            "2x": creator.coffee_price * 2,
            "3x": creator.coffee_price * 3,
            "5x": creator.coffee_price * 5,
        },
    }
    return render(request, "creators_page.html", context)


def creators_list(request):
    creators = CreatorProfile.objects.active_creators().select_related("user")
    search_query = request.GET.get("q", "").strip()
    sort_by = request.GET.get("sort", "").strip()

    creators = creators.search(search_query)
    creators = creators.apply_sort(sort_by)

    # TODO: Add category choices from model
    category_choices = [
        ("all", "All Categories"),
        ("digital_artist", "Digital Artist"),
        ("music_creator", "Music Creator"),
        ("tech_educator", "Tech Educator"),
        ("writer", "Writer"),
        ("gamer", "Gamer"),
    ]

    sort_choices = [
        ("", "Default"),
        ("supporters", "Most Supporters"),
        ("recent", "Recently Added"),
        ("monthly", "Highest Monthly"),
    ]

    context = {
        "creators": creators,
        "search_query": search_query,
        "sort_by": sort_by,
        "category_choices": category_choices,
        "sort_choices": sort_choices,
    }
    return render(request, "creators_list.html", context)


@login_required
def profile_settings(request):
    profile, _created = CreatorProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = CreatorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile have been saved.")
            return redirect("dashboard:profile_settings")
        messages.error(request, "Please correct the errors below.")
    else:
        form = CreatorProfileForm(instance=profile)

    context = {"form": form, "settings": profile}
    context.update(get_kyc_context(request.user))

    return render(request, "profile_settings.html", context)
