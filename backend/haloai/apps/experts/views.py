from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from decimal import Decimal
import json

from .models import (
    ExpertProfile,
    ExpertSpecialization,
    ConsultationRequest,
    ConsultationReview,
    ExpertBlog,
)
from apps.users.models import CustomUser


def experts_list(request):
    """Display list of verified experts with filtering and search"""

    # Get all verified experts
    experts = (
        ExpertProfile.objects.filter(verification_status="verified", is_available=True)
        .select_related("user")
        .prefetch_related("specializations")
    )

    # Search functionality
    search_query = request.GET.get("search")
    if search_query:
        experts = experts.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(professional_title__icontains=search_query)
            | Q(organization__icontains=search_query)
            | Q(specializations__name__icontains=search_query)
        ).distinct()

    # Filter by specialization
    specialization_filter = request.GET.get("specialization")
    if specialization_filter:
        experts = experts.filter(specializations__id=specialization_filter)

    # Filter by location (for in-person consultations)
    location_filter = request.GET.get("location")
    if location_filter:
        experts = experts.filter(service_areas__icontains=location_filter)

    # Filter by consultation mode
    consultation_mode = request.GET.get("mode")
    if consultation_mode:
        experts = experts.filter(consultation_modes__in=[consultation_mode, "both"])

    # Sort options
    sort_by = request.GET.get("sort", "rating")
    if sort_by == "rating":
        experts = experts.order_by("-average_rating", "-total_consultations")
    elif sort_by == "experience":
        experts = experts.order_by("-years_of_experience")
    elif sort_by == "price_low":
        experts = experts.order_by("hourly_rate")
    elif sort_by == "price_high":
        experts = experts.order_by("-hourly_rate")

    # Pagination
    paginator = Paginator(experts, 12)  # Show 12 experts per page
    page_number = request.GET.get("page")
    experts_page = paginator.get_page(page_number)

    # Get all specializations for filter dropdown
    specializations = ExpertSpecialization.objects.filter(is_active=True)

    context = {
        "experts": experts_page,
        "specializations": specializations,
        "search_query": search_query,
        "selected_specialization": specialization_filter,
        "selected_location": location_filter,
        "selected_mode": consultation_mode,
        "sort_by": sort_by,
    }

    return render(request, "experts/experts_list.html", context)


def expert_detail(request, expert_id):
    """Display detailed expert profile"""

    expert = get_object_or_404(
        ExpertProfile, id=expert_id, verification_status="verified"
    )

    # Get recent reviews
    reviews = ConsultationReview.objects.filter(expert=expert).order_by("-created_at")[
        :5
    ]

    # Get recent blog posts by this expert
    blog_posts = ExpertBlog.objects.filter(expert=expert, status="published").order_by(
        "-published_at"
    )[:3]

    # Calculate rating breakdown
    rating_breakdown = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }

    context = {
        "expert": expert,
        "reviews": reviews,
        "blog_posts": blog_posts,
        "rating_breakdown": rating_breakdown,
        "total_reviews": reviews.count(),
    }

    return render(request, "experts/expert_detail.html", context)


@login_required
def book_consultation(request, expert_id):
    """Book a consultation with an expert"""

    expert = get_object_or_404(
        ExpertProfile, id=expert_id, verification_status="verified"
    )

    if request.method == "POST":
        try:
            # Create consultation request
            consultation = ConsultationRequest.objects.create(
                farmer=request.user,
                expert=expert,
                consultation_type=request.POST.get("consultation_type"),
                title=request.POST.get("title"),
                description=request.POST.get("description"),
                preferred_mode=request.POST.get("preferred_mode"),
                preferred_date=request.POST.get("preferred_date"),
                preferred_time=request.POST.get("preferred_time"),
                duration_hours=Decimal(request.POST.get("duration_hours", "1.0")),
                consultation_address=request.POST.get("consultation_address", ""),
            )

            # Calculate cost
            consultation.total_cost = consultation.calculate_cost()
            consultation.save()

            messages.success(
                request,
                "Consultation request sent successfully! The expert will respond soon.",
            )
            return redirect(
                "experts:consultation_detail", consultation_id=consultation.id
            )

        except Exception as e:
            messages.error(request, f"Error booking consultation: {str(e)}")

    context = {
        "expert": expert,
        "consultation_types": ConsultationRequest.CONSULTATION_TYPES,
        "consultation_modes": ExpertProfile.CONSULTATION_MODES,
    }

    return render(request, "experts/book_consultation.html", context)


@login_required
def my_consultations(request):
    """Display user's consultation requests"""

    # Get consultations where user is the farmer
    consultations = (
        ConsultationRequest.objects.filter(farmer=request.user)
        .select_related("expert__user")
        .order_by("-created_at")
    )

    # Filter by status if requested
    status_filter = request.GET.get("status")
    if status_filter:
        consultations = consultations.filter(status=status_filter)

    # Pagination
    paginator = Paginator(consultations, 10)
    page_number = request.GET.get("page")
    consultations_page = paginator.get_page(page_number)

    context = {
        "consultations": consultations_page,
        "status_filter": status_filter,
        "status_choices": ConsultationRequest.STATUS_CHOICES,
    }

    return render(request, "experts/my_consultations.html", context)


@login_required
def consultation_detail(request, consultation_id):
    """Display consultation request details"""

    consultation = get_object_or_404(
        ConsultationRequest, id=consultation_id, farmer=request.user
    )

    context = {
        "consultation": consultation,
    }

    return render(request, "experts/consultation_detail.html", context)


@login_required
def expert_dashboard(request):
    """Dashboard for experts to manage their consultations"""

    # Check if user has expert profile
    try:
        expert_profile = request.user.expert_profile
    except:
        messages.error(request, "You need to create an expert profile first.")
        return redirect("experts:become_expert")

    # Get consultation requests for this expert
    pending_requests = ConsultationRequest.objects.filter(
        expert=expert_profile, status="pending"
    ).order_by("-created_at")

    upcoming_consultations = ConsultationRequest.objects.filter(
        expert=expert_profile, status="accepted", scheduled_datetime__gt=timezone.now()
    ).order_by("scheduled_datetime")

    recent_consultations = ConsultationRequest.objects.filter(
        expert=expert_profile, status__in=["completed", "cancelled"]
    ).order_by("-updated_at")[:10]

    # Statistics
    total_consultations = expert_profile.total_consultations
    pending_count = pending_requests.count()
    this_month_consultations = ConsultationRequest.objects.filter(
        expert=expert_profile,
        status="completed",
        completed_at__month=timezone.now().month,
        completed_at__year=timezone.now().year,
    ).count()

    context = {
        "expert_profile": expert_profile,
        "pending_requests": pending_requests,
        "upcoming_consultations": upcoming_consultations,
        "recent_consultations": recent_consultations,
        "total_consultations": total_consultations,
        "pending_count": pending_count,
        "this_month_consultations": this_month_consultations,
    }

    return render(request, "experts/expert_dashboard.html", context)


@login_required
@require_http_methods(["POST"])
def respond_to_consultation(request, consultation_id):
    """Expert responds to consultation request"""

    consultation = get_object_or_404(
        ConsultationRequest, id=consultation_id, expert__user=request.user
    )

    action = request.POST.get("action")
    response_text = request.POST.get("response_text", "")

    if action == "accept":
        consultation.status = "accepted"
        consultation.expert_response = response_text
        consultation.expert_responded_at = timezone.now()

        # Set scheduled datetime if provided
        scheduled_date = request.POST.get("scheduled_date")
        scheduled_time = request.POST.get("scheduled_time")
        if scheduled_date and scheduled_time:
            scheduled_datetime_str = f"{scheduled_date} {scheduled_time}"
            consultation.scheduled_datetime = timezone.datetime.strptime(
                scheduled_datetime_str, "%Y-%m-%d %H:%M"
            )

        consultation.meeting_link = request.POST.get("meeting_link", "")
        consultation.save()

        messages.success(request, "Consultation request accepted successfully!")

    elif action == "reject":
        consultation.status = "rejected"
        consultation.expert_response = response_text
        consultation.expert_responded_at = timezone.now()
        consultation.save()

        messages.success(request, "Consultation request declined.")

    return redirect("experts:expert_dashboard")


@login_required
def become_expert(request):
    """Apply to become a verified expert"""

    if request.method == "POST":
        try:
            # Create expert profile
            expert_profile = ExpertProfile.objects.create(
                user=request.user,
                professional_title=request.POST.get("professional_title"),
                organization=request.POST.get("organization"),
                years_of_experience=int(request.POST.get("years_of_experience")),
                education_background=request.POST.get("education_background"),
                professional_license=request.POST.get("professional_license"),
                phone_number=request.POST.get("phone_number"),
                consultation_modes=request.POST.get("consultation_modes"),
                hourly_rate=Decimal(request.POST.get("hourly_rate")),
                service_areas=request.POST.get("service_areas"),
                bio=request.POST.get("bio"),
                languages_spoken=request.POST.get("languages_spoken"),
                available_days=request.POST.get("available_days"),
                available_hours=request.POST.get("available_hours"),
            )

            # Add specializations
            specialization_ids = request.POST.getlist("specializations")
            expert_profile.specializations.set(specialization_ids)

            messages.success(
                request,
                "Expert application submitted successfully! We will review your application.",
            )
            return redirect("experts:expert_dashboard")

        except Exception as e:
            messages.error(request, f"Error submitting application: {str(e)}")

    specializations = ExpertSpecialization.objects.filter(is_active=True)

    context = {
        "specializations": specializations,
        "consultation_modes": ExpertProfile.CONSULTATION_MODES,
    }

    return render(request, "experts/become_expert.html", context)


def expert_blog_list(request):
    """Display list of expert blog posts"""

    blog_posts = (
        ExpertBlog.objects.filter(status="published")
        .select_related("expert__user")
        .prefetch_related("specializations")
        .order_by("-published_at")
    )

    # Filter by specialization
    specialization_filter = request.GET.get("specialization")
    if specialization_filter:
        blog_posts = blog_posts.filter(specializations__id=specialization_filter)

    # Search functionality
    search_query = request.GET.get("search")
    if search_query:
        blog_posts = blog_posts.filter(
            Q(title__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(tags__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(blog_posts, 6)
    page_number = request.GET.get("page")
    blog_posts_page = paginator.get_page(page_number)

    specializations = ExpertSpecialization.objects.filter(is_active=True)

    context = {
        "blog_posts": blog_posts_page,
        "specializations": specializations,
        "search_query": search_query,
        "selected_specialization": specialization_filter,
    }

    return render(request, "experts/blog_list.html", context)


def expert_blog_detail(request, slug):
    """Display expert blog post detail"""

    blog_post = get_object_or_404(ExpertBlog, slug=slug, status="published")

    # Increment views count
    blog_post.views_count += 1
    blog_post.save(update_fields=["views_count"])

    # Get related posts
    related_posts = (
        ExpertBlog.objects.filter(
            specializations__in=blog_post.specializations.all(), status="published"
        )
        .exclude(id=blog_post.id)
        .distinct()[:3]
    )

    context = {
        "blog_post": blog_post,
        "related_posts": related_posts,
    }

    return render(request, "experts/blog_detail.html", context)


@login_required
def submit_review(request, consultation_id):
    """Submit review for completed consultation"""

    consultation = get_object_or_404(
        ConsultationRequest, id=consultation_id, farmer=request.user, status="completed"
    )

    # Check if review already exists
    if hasattr(consultation, "review"):
        messages.warning(request, "You have already reviewed this consultation.")
        return redirect("experts:consultation_detail", consultation_id=consultation.id)

    if request.method == "POST":
        try:
            review = ConsultationReview.objects.create(
                consultation=consultation,
                reviewer=request.user,
                expert=consultation.expert,
                rating=int(request.POST.get("rating")),
                title=request.POST.get("title"),
                review_text=request.POST.get("review_text"),
                expertise_rating=int(request.POST.get("expertise_rating")),
                communication_rating=int(request.POST.get("communication_rating")),
                punctuality_rating=int(request.POST.get("punctuality_rating")),
                value_rating=int(request.POST.get("value_rating")),
                would_recommend=request.POST.get("would_recommend") == "on",
                improvement_suggestions=request.POST.get("improvement_suggestions", ""),
            )

            # Update expert's average rating
            expert = consultation.expert
            avg_rating = ConsultationReview.objects.filter(expert=expert).aggregate(
                avg_rating=Avg("rating")
            )["avg_rating"]
            expert.average_rating = avg_rating or 0
            expert.save(update_fields=["average_rating"])

            messages.success(request, "Review submitted successfully!")
            return redirect(
                "experts:consultation_detail", consultation_id=consultation.id
            )

        except Exception as e:
            messages.error(request, f"Error submitting review: {str(e)}")

    context = {
        "consultation": consultation,
    }

    return render(request, "experts/submit_review.html", context)


# AJAX endpoints
@require_http_methods(["GET"])
def get_expert_availability(request, expert_id):
    """Get expert availability for booking calendar (AJAX)"""

    expert = get_object_or_404(ExpertProfile, id=expert_id)
    date = request.GET.get("date")

    if not date:
        return JsonResponse({"error": "Date parameter required"}, status=400)

    # Get available time slots for the date
    # This is a simplified version - in production you'd have more complex availability logic
    available_slots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

    # Filter out booked slots
    booked_consultations = ConsultationRequest.objects.filter(
        expert=expert, scheduled_datetime__date=date, status="accepted"
    )

    booked_slots = [
        consultation.scheduled_datetime.strftime("%H:%M")
        for consultation in booked_consultations
    ]

    available_slots = [slot for slot in available_slots if slot not in booked_slots]

    return JsonResponse(
        {
            "available_slots": available_slots,
            "expert_name": expert.user.get_full_name(),
            "hourly_rate": float(expert.hourly_rate),
        }
    )


# Create your views here.
def experts_and_offers(request):
    """
    Experts and Offers view that renders the experts/technicians page.
    """
    return render(request, "experts/index.html")
