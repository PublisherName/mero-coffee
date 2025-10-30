from django.shortcuts import render


def login(request):
    return render(request, "accounts/login.html", {})


def signup(request):
    return render(request, "accounts/singup.html", {})
