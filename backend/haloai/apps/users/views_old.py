from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import CustomUser, FarmerProfile

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
        assigned_region = request.POST.get("assigned_region")

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
                role="community_admin",  # Default to community admin for public signup
                assigned_region=assigned_region,
                is_approved=False,  # Requires admin approval
            )
            messages.success(
                request,
                "Community Admin account created successfully! Please wait for admin approval.",
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

            if not remember_me:
                request.session.set_expiry(0)

            # Role-based redirect
            user_role = getattr(user, "role", "farmer")
            if user_role == "admin":
                messages.success(
                    request, f"Welcome back, System Administrator {user.first_name}!"
                )
                return redirect("users:admin_dashboard")
            elif user_role == "community_admin":
                messages.success(
                    request, f"Welcome back, Community Admin {user.first_name}!"
                )
                return redirect("users:community_dashboard")
            else:
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect("dashboard:index")
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


@user_passes_test(is_admin)
def admin_dashboard(request):
    """System Admin dashboard - manage all users and platform"""
    # Get statistics
    total_community_admins = CustomUser.objects.filter(role='community_admin').count()
    pending_approvals = CustomUser.objects.filter(role='community_admin', is_approved=False).count()
    total_farmers = FarmerProfile.objects.count()
    
    # Recent activity
    recent_registrations = CustomUser.objects.filter(
        role='community_admin'
    ).order_by('-date_joined')[:5]
    
    context = {
        'total_community_admins': total_community_admins,
        'pending_approvals': pending_approvals,
        'total_farmers': total_farmers,
        'recent_registrations': recent_registrations,
    }
    
    return render(request, 'users/admin_dashboard.html', context)
    stats = {
        "total_users": CustomUser.objects.count(),
        "community_admins": CustomUser.objects.filter(role="community_admin").count(),
        "farmers": CustomUser.objects.filter(role="farmer").count(),
        "pending_approvals": CustomUser.objects.filter(
            role="community_admin", is_approved=False
        ).count(),
    }

    # Recent users
    recent_users = CustomUser.objects.order_by("-created_at")[:10]

    return render(
        request,
        "users/admin_dashboard.html",
        {"stats": stats, "recent_users": recent_users},
    )


@user_passes_test(is_admin)
def manage_community_admins(request):
    """Admin interface to approve/reject Community Admin applications"""
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        try:
            user = CustomUser.objects.get(id=user_id, role='community_admin')
            
            if action == 'approve':
                user.is_approved = True
                user.save()
                messages.success(request, f"Community Admin {user.username} approved successfully.")
            elif action == 'reject':
                user.delete()
                messages.success(request, f"Community Admin application for {user.username} rejected.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
        except Exception as e:
            messages.error(request, f"Error processing request: {e}")
        
        return redirect('users:manage_community_admins')
    
    # Get pending and approved community admins
    pending_admins = CustomUser.objects.filter(
        role='community_admin', 
        is_approved=False
    ).order_by('-date_joined')
    
    approved_admins = CustomUser.objects.filter(
        role='community_admin', 
        is_approved=True
    ).order_by('-date_joined')
    
    context = {
        'pending_admins': pending_admins,
        'approved_admins': approved_admins,
    }
    
    return render(request, 'users/manage_community_admins.html', context)"""System Admin can manage Community Admins"""
    community_admins = CustomUser.objects.filter(role="community_admin").order_by(
        "-created_at"
    )

    # Handle approval
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        user = get_object_or_404(CustomUser, id=user_id, role="community_admin")

        if action == "approve":
            user.is_approved = True
            user.save()
            messages.success(
                request, f"Community Admin {user.username} has been approved."
            )
        elif action == "reject":
            user.delete()
            messages.success(request, f"Community Admin application has been rejected.")

    paginator = Paginator(community_admins, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "users/manage_community_admins.html", {"page_obj": page_obj})


@user_passes_test(is_community_admin)
def community_dashboard(request):
    """Community Admin dashboard - manage farmers in their region"""
    if not request.user.is_approved:
        messages.warning(request, "Your account is still pending approval.")
        return redirect("users:profile")

    # Get farmers managed by this community admin
    managed_farmers = FarmerProfile.objects.filter(community_admin=request.user)

    stats = {
        "total_farmers": managed_farmers.count(),
        "farmers_with_smartphones": managed_farmers.filter(has_smartphone=True).count(),
        "digital_literate_farmers": managed_farmers.exclude(
            digital_literacy_level="none"
        ).count(),
        "region": request.user.assigned_region or "Not Assigned",
    }

    return render(
        request,
        "users/community_dashboard.html",
        {
            "stats": stats,
            "recent_farmers": managed_farmers.order_by("-created_at")[:10],
        },
    )


@user_passes_test(is_community_admin)
def register_farmer(request):
    """Community Admin registers farmers in their region"""
    if not request.user.is_approved:
        messages.error(
            request, "You cannot register farmers until your account is approved."
        )
        return redirect("users:community_dashboard")

    if request.method == "POST":
        # Basic user info
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        email = request.POST.get("email", "")

        # Farm info
        farm_location = request.POST.get("farm_location")
        farm_size_acres = request.POST.get("farm_size_acres")
        primary_crops = request.POST.get("primary_crops")
        has_smartphone = request.POST.get("has_smartphone") == "on"
        digital_literacy_level = request.POST.get("digital_literacy_level")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "users/register_farmer.html")

        try:
            # Create farmer user with default password
            farmer_user = CustomUser.objects.create_user(
                username=username,
                password="farmer123",  # Default password
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                role="farmer",
                is_approved=True,
            )

            # Create farmer profile
            FarmerProfile.objects.create(
                user=farmer_user,
                community_admin=request.user,
                farm_location=farm_location,
                farm_size_acres=farm_size_acres if farm_size_acres else None,
                primary_crops=primary_crops,
                has_smartphone=has_smartphone,
                digital_literacy_level=digital_literacy_level,
            )

            messages.success(
                request, f"Farmer {first_name} {last_name} registered successfully!"
            )
            return redirect("users:manage_farmers")

        except Exception as e:
            messages.error(request, f"Error registering farmer: {e}")

    return render(request, "users/register_farmer.html")


@user_passes_test(is_community_admin)
def manage_farmers(request):
    """Community Admin manages their registered farmers"""
    if not request.user.is_approved:
        return redirect("users:community_dashboard")

    farmers = FarmerProfile.objects.filter(community_admin=request.user)

    # Search functionality
    search_query = request.GET.get("search")
    if search_query:
        farmers = farmers.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(farm_location__icontains=search_query)
            | Q(primary_crops__icontains=search_query)
        )

    paginator = Paginator(farmers, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "users/manage_farmers.html",
        {"page_obj": page_obj, "search_query": search_query},
    )


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
    }

    return render(request, "users/public_landing.html", {"stats": stats})
