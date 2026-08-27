from django.contrib import admin

from .models import Cart, CartItem, Coupon, Order, OrderItem, Wishlist


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "seller_store", "quantity", "unit_price", "line_total"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "buyer", "status", "grand_total", "created_at"]
    list_filter = ["status"]
    search_fields = ["order_number", "buyer__email"]
    inlines = [OrderItemInline]
    readonly_fields = ["id", "order_number", "subtotal", "discount_total", "grand_total", "created_at"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_type", "discount_value", "times_used", "max_uses", "is_active"]
    search_fields = ["code"]


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
