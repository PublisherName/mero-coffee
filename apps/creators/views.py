from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CreatorProfileForm
from .models import CreatorProfile


def profile(request, username):
    creator = get_object_or_404(CreatorProfile, user__username=username)

    supporter_count = creator.supporters.count() if hasattr(creator, "supporters") else 0

    # TODO: Change this to exactual income
    monthly_income = 10000

    context = {
        "creator": {
            "display_name": creator.display_name,
            "bio": creator.bio,
            "supporter_count": supporter_count,
            "monthly_income": monthly_income,
        }
    }
    return render(request, "creators/creators_page.html", context)


def creators_list(request):
    return render(request, "creators/creators_list.html")


@login_required
def profile_settings(request):
    profile, _created = CreatorProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = CreatorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile have been saved.")
            return redirect("dashboard:profile_settings")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CreatorProfileForm(instance=profile)

    return render(request, "dashboard/profile_settings.html", {"form": form, "settings": profile})
