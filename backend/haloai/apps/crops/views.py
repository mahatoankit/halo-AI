from django.shortcuts import render

# Create your views here.
def crop_prediction(request):
    """
    Crop prediction view that renders the crop prediction page.
    """
    return render(request, "crops/index.html")