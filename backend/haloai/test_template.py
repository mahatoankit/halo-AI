#!/usr/bin/env python3
"""
Test experts template loading
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

from django.template.loader import get_template
from django.template import Context, TemplateSyntaxError
from django.test import RequestFactory
from apps.experts.models import ExpertProfile, ExpertSpecialization


def test_experts_list_template():
    """Test the experts_list.html template"""
    print("🧪 Testing experts_list.html template")

    try:
        # Create a mock request
        factory = RequestFactory()
        request = factory.get("/experts/")

        # Load the template
        template = get_template("experts/experts_list.html")
        print("✅ Template loaded successfully")

        # Create minimal context
        context = {
            "request": request,
            "experts": [],
            "specializations": [],
            "is_paginated": False,
        }

        # Try to render
        rendered = template.render(context)
        print("✅ Template rendered successfully")
        print(f"📄 Rendered content length: {len(rendered)} characters")

        return True

    except TemplateSyntaxError as e:
        print(f"❌ Template syntax error: {e}")
        print(f"   Line: {e.source[0].name if e.source else 'Unknown'}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False


if __name__ == "__main__":
    test_experts_list_template()
