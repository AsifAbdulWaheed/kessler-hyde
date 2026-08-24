from django.shortcuts import render
from .models import HomepageContent


def privacy_policy(request):
    return render(request, "core/privacy_policy.html")


def terms_conditions(request):
    return render(request, "core/terms_conditions.html")


def shipping_policy(request):
    return render(request, "core/shipping_policy.html")


def return_policy(request):
    return render(request, "core/return_policy.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
    return render(request, "core/contact.html")