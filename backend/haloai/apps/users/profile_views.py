"""
Enhanced User Profile Views with Firestore Integration
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from services.firestore_user_service import firestore_user_service
from django.utils import timezone


@login_required
def profile_view(request):
    """Display user profile with data from both Django and Firestore"""
    user = request.user

    # Get Firestore profile data
    firestore_profile = firestore_user_service.get_user_profile(user.pk)

    context = {
        "user": user,
        "firestore_profile": firestore_profile,
        "firestore_available": firestore_user_service.is_available(),
    }

    return render(request, "users/profile.html", context)


@login_required
@require_http_methods(["POST"])
def update_profile_view(request):
    """Update user profile in both Django and Firestore"""
    user = request.user

    # Update Django user fields
    user.first_name = request.POST.get("first_name", user.first_name)
    user.last_name = request.POST.get("last_name", user.last_name)
    user.email = request.POST.get("email", user.email)

    # Update custom fields if they exist
    if hasattr(user, "phone"):
        user.phone = request.POST.get("phone", user.phone)
    if hasattr(user, "assigned_region"):
        user.assigned_region = request.POST.get("assigned_region", user.assigned_region)

    try:
        user.save()

        # Update Firestore profile
        if firestore_user_service.is_available():
            update_data = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": getattr(user, "phone", ""),
                "assigned_region": getattr(user, "assigned_region", ""),
                "profile_updated_at": timezone.now(),
            }

            firestore_success = firestore_user_service.update_user_profile(
                user.pk, update_data
            )

            if firestore_success:
                messages.success(request, "Profile updated successfully!")
            else:
                messages.warning(
                    request, "Profile updated locally. Cloud sync will occur shortly."
                )
        else:
            messages.success(request, "Profile updated successfully!")

    except Exception as e:
        messages.error(request, f"Error updating profile: {e}")

    return redirect("users:profile")


@login_required
def community_dashboard_view(request):
    """Community admin dashboard with Firestore data"""
    if not hasattr(request.user, "role") or request.user.role != "community_admin":
        messages.error(request, "Access denied. Community admin role required.")
        return redirect("dashboard:home")

    region = getattr(request.user, "assigned_region", "")

    if not region:
        messages.warning(request, "No assigned region found.")
        return redirect("dashboard:home")

    # Get community data from Firestore
    community_users = []
    community_stats = {}

    if firestore_user_service.is_available():
        community_users = firestore_user_service.get_users_by_region(region)
        community_stats = firestore_user_service.get_community_stats(region)

    context = {
        "region": region,
        "community_users": community_users,
        "community_stats": community_stats,
        "firestore_available": firestore_user_service.is_available(),
    }

    return render(request, "users/community_dashboard.html", context)


@login_required
def api_user_search(request):
    """API endpoint for searching users in Firestore"""
    if not firestore_user_service.is_available():
        return JsonResponse({"error": "Firestore not available"}, status=503)

    # Build search parameters
    search_params = {}

    role = request.GET.get("role")
    if role:
        search_params["role"] = role

    region = request.GET.get("region")
    if region:
        search_params["assigned_region"] = region

    is_approved = request.GET.get("is_approved")
    if is_approved is not None:
        search_params["is_approved"] = is_approved.lower() == "true"

    try:
        users = firestore_user_service.search_users(search_params)

        # Format response
        user_data = []
        for user in users:
            user_data.append(
                {
                    "django_user_id": user.get("django_user_id"),
                    "username": user.get("username"),
                    "email": user.get("email"),
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"),
                    "role": user.get("role"),
                    "assigned_region": user.get("assigned_region"),
                    "is_approved": user.get("is_approved"),
                    "created_at": user.get("created_at"),
                    "last_login": user.get("last_login"),
                }
            )

        return JsonResponse(
            {
                "users": user_data,
                "count": len(user_data),
                "search_params": search_params,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
