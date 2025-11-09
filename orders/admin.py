from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    # Define fields to be displayed and their order
    fields = ('product', 'price', 'quantity', 'size', 'color')
    # Make size and color visible but not editable
    readonly_fields = ('product', 'price', 'size', 'color') 
    extra = 0
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email', 'full_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['email', 'full_name', 'id']
    inlines = [OrderItemInline]

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'default']
    list_filter = ['default', 'country', 'state']
    search_fields = ['user__username', 'full_name', 'address']
