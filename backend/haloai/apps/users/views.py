from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
from .models import CustomUser, FarmerProfile
from apps.sensors.models import IoTSensorSet
from apps.crops.models import CropPredictionRequest
from services.crop_prediction_service import CropPredictionService
from services.firestore_user_service import firestore_user_service

User = get_user_model()


def is_admin(user):
    return user.is_authenticated and getattr(user, "role", None) == "admin"


def is_community_admin(user):
    return user.is_authenticated and getattr(user, "role", None) == "community_admin"


def is_admin_or_community_admin(user):
    user_role = getattr(user, "role", None)
    return user.is_authenticated and (
        user_role == "admin" or user_role == "community_admin"
    )


@csrf_protect
def signup_view(request):
    """Public signup for Community Admins only. Farmers are registered by Community Admins."""
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        phone = request.POST.get("phone")
        assigned_region = request.POST.get("assigned_region", "Bhairahawa-Butwal")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "users/signup.html")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "users/signup.html")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "users/signup.html")

        try:
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                role="community_admin",
                assigned_region=assigned_region,
                is_approved=False,
            )

            # Create extended profile in Firestore
            profile_data = {
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "role": "community_admin",
                "assigned_region": assigned_region,
                "is_approved": False,
                "profile_type": "community_admin",
                "registration_source": "public_signup",
            }

            firestore_success = firestore_user_service.create_user_profile(
                user.pk, profile_data
            )

            if firestore_success:
                messages.success(
                    request,
                    "Community Admin account created successfully! Your profile has been stored securely. Please wait for admin approval.",
                )
            else:
                messages.success(
                    request,
                    "Community Admin account created successfully! Please wait for admin approval. (Profile sync will occur on next login)",
                )

            return redirect("users:login")
        except Exception as e:
            messages.error(request, f"Error creating user: {e}")

    return render(request, "users/signup.html")


@csrf_protect
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember-me")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if community admin needs approval
            if getattr(user, "role", None) == "community_admin" and not getattr(
                user, "is_approved", True
            ):
                messages.error(request, "Your account is pending admin approval.")
                return render(request, "users/login.html")

            login(request, user)

            # Sync user profile with Firestore on login
            try:
                existing_profile = firestore_user_service.get_user_profile(user.pk)
                if not existing_profile:
                    # Create profile if it doesn't exist
                    profile_data = {
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name or "",
                        "last_name": user.last_name or "",
                        "phone": getattr(user, "phone", "") or "",
                        "role": getattr(user, "role", "farmer"),
                        "assigned_region": getattr(user, "assigned_region", "") or "",
                        "is_approved": getattr(user, "is_approved", True),
                        "profile_type": getattr(user, "role", "farmer"),
                        "last_login": user.last_login,
                        "sync_source": "login_sync",
                    }
                    firestore_user_service.create_user_profile(user.pk, profile_data)
                else:
                    # Update last login
                    firestore_user_service.update_user_profile(
                        user.pk,
                        {"last_login": user.last_login, "last_sync": timezone.now()},
                    )
            except Exception as e:
                # Don't fail login if Firestore sync fails
                messages.info(request, "Profile sync will be updated shortly.")

            if not remember_me:
                request.session.set_expiry(0)

            # Role-based redirect
            user_role = getattr(user, "role", "farmer")
            if user_role == "admin":
                return redirect("users:admin_dashboard")
            elif user_role == "community_admin":
                return redirect("users:community_dashboard")
            else:
                return redirect("home:home")

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "users/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home:home")


@login_required
def profile_view(request):
    """User profile view for all authenticated users"""
    return render(request, "users/profile.html", {"user": request.user})


# Admin Views
@user_passes_test(is_admin)
def admin_dashboard(request):
    """System Admin dashboard - manage all users and platform"""
    # Get statistics
    total_community_admins = CustomUser.objects.filter(role="community_admin").count()
    pending_approvals = CustomUser.objects.filter(
        role="community_admin", is_approved=False
    ).count()
    total_farmers = FarmerProfile.objects.count()
    total_sensors = IoTSensorSet.objects.count()

    # Recent activity
    recent_registrations = CustomUser.objects.filter(role="community_admin").order_by(
        "-date_joined"
    )[:5]

    context = {
        "total_community_admins": total_community_admins,
        "pending_approvals": pending_approvals,
        "total_farmers": total_farmers,
        "total_sensors": total_sensors,
        "recent_registrations": recent_registrations,
    }

    return render(request, "users/admin_dashboard.html", context)


@user_passes_test(is_admin)
def manage_community_admins(request):
    """Admin interface to approve/reject Community Admin applications"""
    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")

        try:
            user = CustomUser.objects.get(id=user_id, role="community_admin")

            if action == "approve":
                user.is_approved = True
                user.save()
                messages.success(
                    request, f"Community Admin {user.username} approved successfully."
                )
            elif action == "reject":
                user.delete()
                messages.success(
                    request,
                    f"Community Admin application for {user.username} rejected.",
                )
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
        except Exception as e:
            messages.error(request, f"Error processing request: {e}")

        return redirect("users:manage_community_admins")

    # Get pending and approved community admins
    pending_admins = CustomUser.objects.filter(
        role="community_admin", is_approved=False
    ).order_by("-date_joined")

    approved_admins = CustomUser.objects.filter(
        role="community_admin", is_approved=True
    ).order_by("-date_joined")

    context = {
        "pending_admins": pending_admins,
        "approved_admins": approved_admins,
    }

    return render(request, "users/manage_community_admins.html", context)


# Community Admin Views
@user_passes_test(is_community_admin)
def community_dashboard(request):
    """Community Admin dashboard - manage sensors and predictions for their region"""
    community_admin = request.user

    # Get managed sensors
    managed_sensors = IoTSensorSet.objects.filter(
        community_admin=community_admin
    ).order_by("-created_at")

    # Get managed farmers
    managed_farmers = FarmerProfile.objects.filter(
        community_admin=community_admin
    ).order_by("-created_at")

    # Get recent predictions
    recent_predictions = CropPredictionRequest.objects.filter(
        community_admin=community_admin
    ).order_by("-requested_at")[:5]

    # Get statistics
    stats = {
        "total_sensors": managed_sensors.count(),
        "active_sensors": managed_sensors.filter(status="active").count(),
        "total_farmers": managed_farmers.count(),
        "total_predictions": CropPredictionRequest.objects.filter(
            community_admin=community_admin
        ).count(),
        "region": community_admin.assigned_region or "Bhairahawa-Butwal",
    }

    context = {
        "community_admin": community_admin,
        "managed_sensors": managed_sensors[:5],  # Show latest 5
        "managed_farmers": managed_farmers[:5],  # Show latest 5
        "recent_predictions": recent_predictions,
        "stats": stats,
    }

    return render(request, "users/community_dashboard.html", context)


@user_passes_test(is_community_admin)
def register_farmer(request):
    """Community Admin registers farmers in their region"""
    if request.method == "POST":
        # Create farmer user
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")

        # Farmer profile data
        farm_location = request.POST.get("farm_location")
        farm_size_acres = request.POST.get("farm_size_acres")
        primary_crops = request.POST.get("primary_crops")
        has_smartphone = request.POST.get("has_smartphone") == "on"
        digital_literacy_level = request.POST.get("digital_literacy_level")

        try:
            # Create farmer user
            farmer_user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role="farmer",
                is_approved=True,  # Auto-approved when registered by Community Admin
            )

            # Create farmer profile
            FarmerProfile.objects.create(
                user=farmer_user,
                community_admin=request.user,
                farm_location=farm_location,
                farm_size_acres=float(farm_size_acres) if farm_size_acres else None,
                primary_crops=primary_crops,
                has_smartphone=has_smartphone,
                digital_literacy_level=digital_literacy_level,
            )

            messages.success(
                request,
                f"Farmer {farmer_user.get_full_name()} registered successfully!",
            )
            return redirect("users:manage_farmers")

        except Exception as e:
            messages.error(request, f"Error registering farmer: {e}")

    return render(request, "users/register_farmer.html")


@user_passes_test(is_community_admin)
def manage_farmers(request):
    """Community Admin manages their registered farmers"""
    community_admin = request.user

    # Get search query
    search_query = request.GET.get("q", "")

    farmers = FarmerProfile.objects.filter(community_admin=community_admin)

    if search_query:
        farmers = farmers.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(user__username__icontains=search_query)
            | Q(farm_location__icontains=search_query)
            | Q(primary_crops__icontains=search_query)
        )

    farmers = farmers.order_by("-created_at")

    # Pagination
    paginator = Paginator(farmers, 10)
    page_number = request.GET.get("page")
    farmers_page = paginator.get_page(page_number)

    context = {
        "farmers": farmers_page,
        "search_query": search_query,
        "total_farmers": farmers.count(),
        "community_admin": community_admin,
    }

    return render(request, "users/manage_farmers.html", context)


def public_landing(request):
    """Public landing page accessible to all without authentication"""
    # Aggregated, non-sensitive statistics
    stats = {
        "total_communities": CustomUser.objects.filter(
            role="community_admin", is_approved=True
        ).count(),
        "total_farmers_helped": FarmerProfile.objects.count(),
        "regions_covered": CustomUser.objects.filter(
            role="community_admin", is_approved=True, assigned_region__isnull=False
        )
        .exclude(assigned_region="")
        .values("assigned_region")
        .distinct()
        .count(),
        "total_predictions": CropPredictionRequest.objects.filter(
            status="completed"
        ).count(),
    }

    return render(request, "users/public_landing.html", {"stats": stats})
