from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def community_dashboard(request):
    """
    Community Dashboard view that renders the community dashboard page.
    """
    context = {
        "title": "Community Dashboard",
        "description": "Connect with fellow farmers, share insights, and grow together.",
        "user": request.user,
    }
    return render(request, "dashboard/index.html", context)
