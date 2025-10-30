from django.shortcuts import render


def profile(request):
    return render(request, "creators/creators_page.html", {})


def creators_list(request):
    return render(request, "creators/creators_list.html")
