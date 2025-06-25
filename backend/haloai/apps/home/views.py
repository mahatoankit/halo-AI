from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    """Home page view with context data"""
    # context = {"title": "Welcome to HaloAI", "message": "Smart Agriculture Platform"}
    return render(request, "home/index.html")
