#!/usr/bin/env python
"""
Test script to validate the marketplace functionality.
Tests URL patterns, view responses, and template rendering.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from apps.marketplace.models import Category, Vendor, Product
from apps.users.models import CustomUser


def test_marketplace_urls():
    """Test all marketplace URL patterns"""
    client = Client()

    print("🧪 Testing Marketplace URLs...")
    print("=" * 50)

    # Test URLs without authentication first
    public_urls = [
        ("marketplace:home", "Marketplace Home"),
        ("marketplace:product_list", "Product List"),
    ]

    for url_name, description in public_urls:
        try:
            url = reverse(url_name)
            response = client.get(url)
            print(f"✅ {description}: {url} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {description}: Error - {str(e)}")

    # Create test user for authenticated tests
    try:
        user = CustomUser.objects.filter(email="testfarmer@example.com").first()
        if not user:
            user = CustomUser.objects.create_user(
                email="testfarmer@example.com",
                username="testfarmer",
                password="testpass123",
                first_name="Test",
                last_name="Farmer",
                role="farmer",
            )
            print(f"📝 Created test user: {user.email}")

        # Login
        client.login(email="testfarmer@example.com", password="testpass123")
        print(f"🔐 Logged in as: {user.email}")

        # Test authenticated URLs
        auth_urls = [
            ("marketplace:home", "Marketplace Home (Auth)"),
            ("marketplace:product_list", "Product List (Auth)"),
            ("marketplace:cart", "Shopping Cart"),
            ("marketplace:cart_count", "Cart Count API"),
            ("marketplace:checkout", "Checkout"),
            ("marketplace:order_history", "Order History"),
        ]

        for url_name, description in auth_urls:
            try:
                url = reverse(url_name)
                response = client.get(url)
                print(f"✅ {description}: {url} (Status: {response.status_code})")
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")

        # Test product detail with sample product
        try:
            product = Product.objects.first()
            if product:
                url = reverse("marketplace:product_detail", args=[product.id])
                response = client.get(url)
                print(f"✅ Product Detail: {url} (Status: {response.status_code})")
            else:
                print(f"⚠️  No products found for detail test")
        except Exception as e:
            print(f"❌ Product Detail: Error - {str(e)}")

    except Exception as e:
        print(f"❌ Authentication setup failed: {str(e)}")


def test_marketplace_data():
    """Test marketplace data existence"""
    print("\n📊 Testing Marketplace Data...")
    print("=" * 50)

    # Test categories
    categories = Category.objects.all()
    print(f"📁 Categories: {categories.count()}")
    for cat in categories:
        print(f"   - {cat.icon} {cat.name}")

    # Test vendors
    vendors = Vendor.objects.all()
    print(f"\n🏪 Vendors: {vendors.count()}")
    for vendor in vendors:
        verified = "✅" if vendor.is_verified else "⚠️"
        print(f"   - {verified} {vendor.name} ({vendor.region})")

    # Test products
    products = Product.objects.all()
    print(f"\n📦 Products: {products.count()}")

    product_types = {}
    for product in products:
        if product.product_type not in product_types:
            product_types[product.product_type] = 0
        product_types[product.product_type] += 1

    for product_type, count in product_types.items():
        print(f"   - {product_type.replace('_', ' ').title()}: {count} products")

    # Test featured products
    featured = Product.objects.filter(is_featured=True)
    print(f"\n⭐ Featured Products: {featured.count()}")
    for product in featured[:5]:  # Show first 5
        print(f"   - {product.name} - Rs.{product.price}")


def test_marketplace_api():
    """Test marketplace API endpoints"""
    print("\n🔌 Testing Marketplace API...")
    print("=" * 50)

    client = Client()

    # Create and login test user
    user = CustomUser.objects.filter(email="testfarmer@example.com").first()
    if user:
        client.login(email="testfarmer@example.com", password="testpass123")

        # Test cart count API
        try:
            response = client.get(reverse("marketplace:cart_count"))
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Cart Count API: {data}")
            else:
                print(f"❌ Cart Count API: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Cart Count API: Error - {str(e)}")

        # Test add to cart API
        try:
            product = Product.objects.first()
            if product:
                response = client.post(
                    reverse("marketplace:add_to_cart"),
                    {"product_id": product.id, "quantity": 2},
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Add to Cart API: {data}")
                else:
                    print(f"❌ Add to Cart API: Status {response.status_code}")
            else:
                print(f"⚠️  No products found for cart test")
        except Exception as e:
            print(f"❌ Add to Cart API: Error - {str(e)}")


def main():
    """Main test function"""
    print("🛒 MARKETPLACE TESTING SUITE")
    print("=" * 50)

    test_marketplace_data()
    test_marketplace_urls()
    test_marketplace_api()

    print("\n" + "=" * 50)
    print("✅ Marketplace testing completed!")
    print(f"📊 Total Categories: {Category.objects.count()}")
    print(f"🏪 Total Vendors: {Vendor.objects.count()}")
    print(f"📦 Total Products: {Product.objects.count()}")
    print(f"⭐ Featured Products: {Product.objects.filter(is_featured=True).count()}")


if __name__ == "__main__":
    main()
