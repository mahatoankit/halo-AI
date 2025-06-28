#!/usr/bin/env python
"""
Script to populate the marketplace with sample data for demonstration.
Creates categories, vendors, and products with realistic data.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from apps.marketplace.models import Category, Vendor, Product
from apps.users.models import CustomUser


def create_categories():
    """Create product categories"""
    categories_data = [
        {
            "name": "Seeds & Seedlings",
            "description": "High-quality seeds and seedlings for various crops",
            "icon": "🌱",
        },
        {
            "name": "Fertilizers & Nutrients",
            "description": "Organic and chemical fertilizers for soil enrichment",
            "icon": "🌿",
        },
        {
            "name": "Pesticides & Herbicides",
            "description": "Plant protection products for pest and weed control",
            "icon": "🛡️",
        },
        {
            "name": "Farm Tools & Equipment",
            "description": "Essential tools and equipment for farming operations",
            "icon": "🔧",
        },
        {
            "name": "Irrigation Systems",
            "description": "Water management and irrigation solutions",
            "icon": "💧",
        },
        {
            "name": "Organic Products",
            "description": "Certified organic farming inputs and products",
            "icon": "🌾",
        },
        {
            "name": "AgriTech & IoT",
            "description": "Modern technology solutions for smart farming",
            "icon": "📡",
        },
    ]

    print("Creating categories...")
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"], defaults=cat_data
        )
        if created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"⚠️  Category exists: {category.name}")


def create_vendors():
    """Create sample vendors"""
    vendors_data = [
        {
            "name": "Bhairahawa Agri Supplies",
            "description": "Leading supplier of agricultural inputs in Bhairahawa region",
            "contact_email": "info@bhairahawa-agri.com",
            "contact_phone": "+977-71-520001",
            "address": "Bhairahawa-11, Rupandehi, Nepal",
            "region": "Bhairahawa-Butwal",
            "is_verified": True,
            "commission_rate": Decimal("8.50"),
        },
        {
            "name": "Butwal Farm Center",
            "description": "Complete farming solutions with 20+ years of experience",
            "contact_email": "sales@butwalfarm.com",
            "contact_phone": "+977-71-540002",
            "address": "Butwal-19, Rupandehi, Nepal",
            "region": "Bhairahawa-Butwal",
            "is_verified": True,
            "commission_rate": Decimal("10.00"),
        },
        {
            "name": "Lumbini Seeds Company",
            "description": "Premium quality seeds and seedlings for all crops",
            "contact_email": "contact@lumbinieeds.com",
            "contact_phone": "+977-71-580003",
            "address": "Lumbini-5, Rupandehi, Nepal",
            "region": "Bhairahawa-Butwal",
            "is_verified": True,
            "commission_rate": Decimal("12.00"),
        },
        {
            "name": "Modern Agri Tech",
            "description": "Cutting-edge agricultural technology and IoT solutions",
            "contact_email": "info@modernagritech.com",
            "contact_phone": "+977-71-560004",
            "address": "Siddharthanagar-7, Rupandehi, Nepal",
            "region": "Bhairahawa-Butwal",
            "is_verified": True,
            "commission_rate": Decimal("15.00"),
        },
        {
            "name": "Organic Nepal",
            "description": "Certified organic farming products and consulting",
            "contact_email": "info@organicnepal.com",
            "contact_phone": "+977-71-590005",
            "address": "Devdaha-3, Rupandehi, Nepal",
            "region": "Bhairahawa-Butwal",
            "is_verified": True,
            "commission_rate": Decimal("9.00"),
        },
    ]

    print("Creating vendors...")
    for vendor_data in vendors_data:
        vendor, created = Vendor.objects.get_or_create(
            name=vendor_data["name"], defaults=vendor_data
        )
        if created:
            print(f"✅ Created vendor: {vendor.name}")
        else:
            print(f"⚠️  Vendor exists: {vendor.name}")


def create_products():
    """Create sample products"""
    # Get categories and vendors
    categories = {cat.name: cat for cat in Category.objects.all()}
    vendors = {vendor.name: vendor for vendor in Vendor.objects.all()}

    products_data = [
        # Seeds & Seedlings
        {
            "name": "Hybrid Tomato Seeds (Srijana)",
            "category": categories["Seeds & Seedlings"],
            "vendor": vendors["Lumbini Seeds Company"],
            "product_type": "seeds",
            "description": "High-yielding hybrid tomato seeds suitable for both tunnel and open field cultivation. Disease resistant variety with excellent fruit quality.",
            "price": Decimal("450.00"),
            "unit": "10g packet",
            "stock_quantity": 150,
            "min_order_quantity": 5,
            "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400",
            "is_featured": True,
        },
        {
            "name": "Cauliflower Seeds (Snowball)",
            "category": categories["Seeds & Seedlings"],
            "vendor": vendors["Lumbini Seeds Company"],
            "product_type": "seeds",
            "description": "Premium quality cauliflower seeds with excellent head formation and disease resistance.",
            "price": Decimal("320.00"),
            "unit": "10g packet",
            "stock_quantity": 200,
            "min_order_quantity": 3,
            "image_url": "https://images.unsplash.com/photo-1568584711271-946d4d069da9?w=400",
            "is_featured": True,
        },
        {
            "name": "Mustard Seeds (Rayo)",
            "category": categories["Seeds & Seedlings"],
            "vendor": vendors["Bhairahawa Agri Supplies"],
            "product_type": "seeds",
            "description": "Local variety mustard seeds perfect for oil production and vegetable cultivation.",
            "price": Decimal("180.00"),
            "unit": "1kg",
            "stock_quantity": 500,
            "min_order_quantity": 10,
            "image_url": "https://images.unsplash.com/photo-1605027922433-b0fa5c2c1d3a?w=400",
            "is_featured": False,
        },
        # Fertilizers & Nutrients
        {
            "name": "NPK Fertilizer (20:20:20)",
            "category": categories["Fertilizers & Nutrients"],
            "vendor": vendors["Bhairahawa Agri Supplies"],
            "product_type": "fertilizers",
            "description": "Balanced NPK fertilizer suitable for all types of crops. Provides essential nutrients for healthy plant growth.",
            "price": Decimal("2800.00"),
            "unit": "50kg bag",
            "stock_quantity": 100,
            "min_order_quantity": 2,
            "image_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400",
            "is_featured": True,
        },
        {
            "name": "Urea Fertilizer",
            "category": categories["Fertilizers & Nutrients"],
            "vendor": vendors["Butwal Farm Center"],
            "product_type": "fertilizers",
            "description": "High-quality urea fertilizer for nitrogen supplementation. Ideal for leafy vegetables and cereals.",
            "price": Decimal("1850.00"),
            "unit": "50kg bag",
            "stock_quantity": 80,
            "min_order_quantity": 2,
            "image_url": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400",
            "is_featured": False,
        },
        {
            "name": "Vermicompost",
            "category": categories["Organic Products"],
            "vendor": vendors["Organic Nepal"],
            "product_type": "organic",
            "description": "Premium quality vermicompost made from earthworms. Rich in nutrients and beneficial microorganisms.",
            "price": Decimal("800.00"),
            "unit": "25kg bag",
            "stock_quantity": 200,
            "min_order_quantity": 4,
            "image_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400",
            "is_featured": True,
        },
        # Pesticides & Herbicides
        {
            "name": "Dimethoate Insecticide",
            "category": categories["Pesticides & Herbicides"],
            "vendor": vendors["Bhairahawa Agri Supplies"],
            "product_type": "pesticides",
            "description": "Effective systemic insecticide for controlling aphids, thrips, and other sucking pests.",
            "price": Decimal("1200.00"),
            "unit": "1 liter",
            "stock_quantity": 50,
            "min_order_quantity": 1,
            "image_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5d?w=400",
            "is_featured": False,
        },
        {
            "name": "Neem Oil",
            "category": categories["Organic Products"],
            "vendor": vendors["Organic Nepal"],
            "product_type": "organic",
            "description": "Organic neem oil for natural pest control. Safe for humans and beneficial insects.",
            "price": Decimal("650.00"),
            "unit": "500ml bottle",
            "stock_quantity": 120,
            "min_order_quantity": 2,
            "image_url": "https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400",
            "is_featured": True,
        },
        # Farm Tools & Equipment
        {
            "name": "Garden Hoe (Kodalo)",
            "category": categories["Farm Tools & Equipment"],
            "vendor": vendors["Butwal Farm Center"],
            "product_type": "tools",
            "description": "Traditional Nepali garden hoe made from high-quality steel. Perfect for soil preparation and weeding.",
            "price": Decimal("1200.00"),
            "unit": "piece",
            "stock_quantity": 75,
            "min_order_quantity": 1,
            "image_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400",
            "is_featured": False,
        },
        {
            "name": "Pruning Shears",
            "category": categories["Farm Tools & Equipment"],
            "vendor": vendors["Butwal Farm Center"],
            "product_type": "tools",
            "description": "Professional-grade pruning shears for fruit trees and ornamental plants. Sharp and durable.",
            "price": Decimal("850.00"),
            "unit": "piece",
            "stock_quantity": 60,
            "min_order_quantity": 1,
            "image_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400",
            "is_featured": False,
        },
        {
            "name": "Power Tiller (8HP)",
            "category": categories["Farm Tools & Equipment"],
            "vendor": vendors["Modern Agri Tech"],
            "product_type": "tools",
            "description": "Reliable 8HP power tiller for soil preparation, plowing, and cultivation. Suitable for small to medium farms.",
            "price": Decimal("185000.00"),
            "unit": "piece",
            "stock_quantity": 5,
            "min_order_quantity": 1,
            "image_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5d?w=400",
            "is_featured": True,
        },
        # Irrigation Systems
        {
            "name": "Drip Irrigation Kit (1 Ropani)",
            "category": categories["Irrigation Systems"],
            "vendor": vendors["Modern Agri Tech"],
            "product_type": "irrigation",
            "description": "Complete drip irrigation system for 1 ropani (0.05 hectare). Includes pipes, emitters, and fittings.",
            "price": Decimal("25000.00"),
            "unit": "kit",
            "stock_quantity": 15,
            "min_order_quantity": 1,
            "image_url": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400",
            "is_featured": True,
        },
        {
            "name": "Sprinkler Irrigation Head",
            "category": categories["Irrigation Systems"],
            "vendor": vendors["Butwal Farm Center"],
            "product_type": "irrigation",
            "description": "Adjustable sprinkler head for efficient water distribution. Covers up to 8-meter radius.",
            "price": Decimal("1500.00"),
            "unit": "piece",
            "stock_quantity": 40,
            "min_order_quantity": 2,
            "image_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400",
            "is_featured": False,
        },
        # AgriTech & IoT
        {
            "name": "Soil Moisture Sensor",
            "category": categories["AgriTech & IoT"],
            "vendor": vendors["Modern Agri Tech"],
            "product_type": "technology",
            "description": "Digital soil moisture sensor with LCD display. Helps optimize irrigation scheduling.",
            "price": Decimal("3500.00"),
            "unit": "piece",
            "stock_quantity": 25,
            "min_order_quantity": 1,
            "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400",
            "is_featured": True,
        },
        {
            "name": "Weather Station (Basic)",
            "category": categories["AgriTech & IoT"],
            "vendor": vendors["Modern Agri Tech"],
            "product_type": "technology",
            "description": "Compact weather station measuring temperature, humidity, and rainfall. Wireless data transmission.",
            "price": Decimal("12000.00"),
            "unit": "piece",
            "stock_quantity": 8,
            "min_order_quantity": 1,
            "image_url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=400",
            "is_featured": True,
        },
        {
            "name": "pH Meter (Digital)",
            "category": categories["AgriTech & IoT"],
            "vendor": vendors["Modern Agri Tech"],
            "product_type": "technology",
            "description": "Portable digital pH meter for soil and water testing. Essential for nutrient management.",
            "price": Decimal("4500.00"),
            "unit": "piece",
            "stock_quantity": 30,
            "min_order_quantity": 1,
            "image_url": "https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400",
            "is_featured": False,
        },
    ]

    print("Creating products...")
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data["name"], defaults=product_data
        )
        if created:
            print(f"✅ Created product: {product.name} - Rs.{product.price}")
        else:
            print(f"⚠️  Product exists: {product.name}")


def main():
    """Main function to create all sample data"""
    print("🛒 Creating marketplace sample data...")
    print("=" * 50)

    create_categories()
    print()
    create_vendors()
    print()
    create_products()

    print("\n" + "=" * 50)
    print("✅ Marketplace sample data creation completed!")
    print(f"📊 Created {Category.objects.count()} categories")
    print(f"🏪 Created {Vendor.objects.count()} vendors")
    print(f"📦 Created {Product.objects.count()} products")
    print(f"⭐ Featured products: {Product.objects.filter(is_featured=True).count()}")


if __name__ == "__main__":
    main()
