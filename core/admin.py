from django.contrib import admin
from .models import Pizza, Order, OrderItem

@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'phone', 'address', 'total', 'created_at')
    search_fields = ('phone', 'address')
    inlines = [OrderItemInline]