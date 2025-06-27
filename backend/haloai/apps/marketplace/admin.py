from django.contrib import admin
from .models import Category, Vendor, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'is_verified', 'commission_rate', 'created_at']
    list_filter = ['is_verified', 'region']
    search_fields = ['name', 'contact_email']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'vendor', 'price', 'stock_quantity', 'is_available']
    list_filter = ['category', 'product_type', 'is_available', 'is_featured']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock_quantity', 'is_available']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'farmer', 'status', 'total_amount', 'commission_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'farmer__username', 'farmer__first_name', 'farmer__last_name']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'commission_amount']