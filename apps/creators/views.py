from django.shortcuts import get_object_or_404, render

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
