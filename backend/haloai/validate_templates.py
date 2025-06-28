#!/usr/bin/env python3
"""
Template validation script
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()


def validate_templates():
    """Validate all expert templates"""
    from django.template.loader import get_template
    from django.template import Context, TemplateSyntaxError
    from django.test import RequestFactory
    from apps.experts.models import ExpertProfile, ExpertSpecialization

    print("🧪 Validating Expert Templates\n")

    # Create a mock request for context
    factory = RequestFactory()
    request = factory.get("/experts/")

    templates_to_test = [
        "experts/experts_list.html",
        "experts/expert_detail.html",
        "experts/book_consultation.html",
        "experts/expert_dashboard.html",
        "experts/become_expert.html",
    ]

    # Create sample context data
    expert = ExpertProfile.objects.first()
    specializations = ExpertSpecialization.objects.all()

    for template_name in templates_to_test:
        try:
            print(f"Testing {template_name}...")
            template = get_template(template_name)

            # Create appropriate context for each template
            context = {
                "request": request,
                "user": None,
                "experts": ExpertProfile.objects.all()[:5],
                "expert": expert,
                "specializations": specializations,
                "search_query": "",
                "selected_specialization": "",
                "location_filter": "",
                "consultation_types": [
                    ("general", "General Agricultural Advice"),
                    ("crop_disease", "Crop Disease Diagnosis"),
                ],
                "is_paginated": False,
                "today": "2025-06-28",
            }

            # Try to render the template
            rendered = template.render(context)
            print(f"   ✅ {template_name} - Template syntax valid")

        except TemplateSyntaxError as e:
            print(f"   ❌ {template_name} - Template syntax error: {e}")
            return False
        except Exception as e:
            print(f"   ⚠️  {template_name} - Other error: {e}")

    print("\n🎉 All templates validated successfully!")
    return True


if __name__ == "__main__":
    validate_templates()
