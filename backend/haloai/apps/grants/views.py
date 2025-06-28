from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, F
from .models import Grant, GrantCategory


# Create your views here.
@login_required
def grants_and_offers(request):
    """
    Grants and Offers view that renders the grants and offers page with database-driven content.
    """
    # Get filter parameters
    category_filter = request.GET.get("category", "all")
    search_query = request.GET.get("search", "")

    # Base queryset
    grants = Grant.objects.filter(is_active=True).select_related("category")

    # Apply category filter
    if category_filter != "all":
        grants = grants.filter(category__name__iexact=category_filter)

    # Apply search filter
    if search_query:
        grants = grants.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(eligibility__icontains=search_query)
        )

    # Get all categories for filter buttons
    categories = GrantCategory.objects.filter(is_active=True).order_by("name")

    # Featured grants for hero section
    featured_grants = Grant.objects.filter(is_active=True, is_featured=True)[:3]

    context = {
        "grants": grants,
        "categories": categories,
        "featured_grants": featured_grants,
        "current_category": category_filter,
        "search_query": search_query,
        "total_grants": grants.count(),
    }

    return render(request, "grants/index.html", context)


@login_required
def grant_detail(request, grant_id):
    """
    Detailed view of a specific grant.
    """
    grant = get_object_or_404(Grant, id=grant_id, is_active=True)

    # Increment view count
    Grant.objects.filter(id=grant_id).update(views_count=F("views_count") + 1)

    # Get related grants from same category
    related_grants = Grant.objects.filter(
        category=grant.category, is_active=True
    ).exclude(id=grant_id)[:3]

    context = {
        "grant": grant,
        "related_grants": related_grants,
    }

    return render(request, "grants/grant_detail.html", context)


def grants_api(request):
    """
    API endpoint for AJAX filtering of grants.
    """
    category = request.GET.get("category", "all")
    search = request.GET.get("search", "")

    grants = Grant.objects.filter(is_active=True).select_related("category")

    if category != "all":
        grants = grants.filter(category__name__iexact=category)

    if search:
        grants = grants.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    grants_data = []
    for grant in grants:
        grants_data.append(
            {
                "id": grant.id,
                "title": grant.title,
                "description": grant.description,
                "category": grant.category.name,
                "category_icon": grant.category.icon,
                "category_color": grant.category.color_class,
                "amount": grant.amount,
                "status_text": grant.status_text,
                "priority": grant.priority,
                "is_featured": grant.is_featured,
                "eligibility": grant.eligibility,
                "application_url": grant.application_url,
            }
        )

    return JsonResponse({"grants": grants_data, "total": len(grants_data)})
