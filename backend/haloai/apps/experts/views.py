from django.shortcuts import render

# Create your views here.
def experts_and_offers(request):
    """
    Experts and Offers view that renders the experts/technicians page.
    """
    return render(request, "experts/index.html")