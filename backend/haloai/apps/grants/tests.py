from django.test import TestCase
from django.urls import path, include

# Create your tests here.
urlpatterns = [
    path('grants/', include('grants.urls', namespace='grants')),
]