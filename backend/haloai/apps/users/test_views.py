"""
Simple view for testing authentication
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import json

User = get_user_model()


def test_login_page(request):
    """Simple page to test authentication"""
    users = User.objects.all()
    user_list = []

    for user in users:
        user_list.append(
            {
                "username": user.username,
                "role": getattr(user, "role", "N/A"),
                "email": user.email,
                "is_active": user.is_active,
                "is_approved": getattr(user, "is_approved", True),
            }
        )

    return render(request, "users/test_login.html", {"users": user_list})


@csrf_exempt
def test_auth_api(request):
    """API endpoint to test authentication"""
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        try:
            # Check if user exists
            user = User.objects.get(username=username)

            # Test authentication
            auth_user = authenticate(username=username, password=password)

            if auth_user:
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Authentication successful",
                        "user_id": auth_user.pk,
                        "username": auth_user.username,
                        "role": getattr(auth_user, "role", "N/A"),
                        "email": auth_user.email,
                    }
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Invalid credentials",
                        "user_exists": True,
                    }
                )

        except User.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "User not found", "user_exists": False}
            )

    return JsonResponse({"error": "POST method required"})
