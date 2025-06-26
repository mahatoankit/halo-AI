from django.urls import path
from . import views
from . import profile_views
from . import test_views

app_name = "users"

urlpatterns = [
    # Public routes
    path("", views.public_landing, name="public_landing"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Test routes (for debugging)
    path("test-login/", test_views.test_login_page, name="test_login"),
    path("test-auth/", test_views.test_auth_api, name="test_auth_api"),
    # Enhanced profile routes with Firestore
    path("profile/", profile_views.profile_view, name="profile"),
    path("profile/update/", profile_views.update_profile_view, name="update_profile"),
    path(
        "community/firestore-dashboard/",
        profile_views.community_dashboard_view,
        name="firestore_dashboard",
    ),
    # API routes
    path("api/search/", profile_views.api_user_search, name="api_search"),
    # Legacy profile route (fallback)
    path("profile-legacy/", views.profile_view, name="profile_legacy"),
    # Admin routes
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path(
        "admin/community-admins/",
        views.manage_community_admins,
        name="manage_community_admins",
    ),
    # Community Admin routes
    path("community/dashboard/", views.community_dashboard, name="community_dashboard"),
    path("community/register-farmer/", views.register_farmer, name="register_farmer"),
    path("community/manage-farmers/", views.manage_farmers, name="manage_farmers"),
]
