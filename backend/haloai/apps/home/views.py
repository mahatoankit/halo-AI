from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def public_landing(request):
    """Public landing page accessible to everyone"""
    context = {
        "title": "Halo AI - Smart Agriculture Platform",
        "description": "Empowering farmers with AI-driven insights for better yields and sustainable agriculture.",
    }
    return render(request, "home/public_landing.html", context)



@login_required
def home(request):
    """Protected home/dashboard page for authenticated users"""
    context = {
        "title": "Welcome to HaloAI Dashboard",
        "user": request.user,
    }
    return render(request, "home/dashboard.html", context)
