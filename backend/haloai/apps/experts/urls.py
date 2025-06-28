from django.urls import path
from . import views

app_name = "experts"

urlpatterns = [
    # Main experts pages
    path("", views.experts_list, name="experts_list"),
    path("expert/<int:expert_id>/", views.expert_detail, name="expert_detail"),
    # Consultation booking and management
    path("book/<int:expert_id>/", views.book_consultation, name="book_consultation"),
    path("my-consultations/", views.my_consultations, name="my_consultations"),
    path(
        "consultation/<uuid:consultation_id>/",
        views.consultation_detail,
        name="consultation_detail",
    ),
    path(
        "consultation/<uuid:consultation_id>/review/",
        views.submit_review,
        name="submit_review",
    ),
    # Expert dashboard and management
    path("dashboard/", views.expert_dashboard, name="expert_dashboard"),
    path("become-expert/", views.become_expert, name="become_expert"),
    path(
        "respond/<uuid:consultation_id>/",
        views.respond_to_consultation,
        name="respond_to_consultation",
    ),
    # Expert blog/knowledge sharing
    path("blog/", views.expert_blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.expert_blog_detail, name="blog_detail"),
    # AJAX endpoints
    path(
        "api/availability/<int:expert_id>/",
        views.get_expert_availability,
        name="get_expert_availability",
    ),
    # Legacy/backward compatibility
    path("index/", views.experts_and_offers, name="index"),
]
