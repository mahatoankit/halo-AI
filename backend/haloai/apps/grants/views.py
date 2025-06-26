from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def grants_and_offers(request):
    """
    Grants and Offers view that renders the grants and offers page.
    """
    return render(request, "grants/index.html")
