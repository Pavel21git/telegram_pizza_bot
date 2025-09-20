from rest_framework import serializers
from .models import Pizza, Order, OrderItem

class PizzaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pizza
        fields = ["id", "name", "description", "price"]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "order", "pizza", "qty", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)   # related_name='items' в модели
    class Meta:
        model = Order
        fields = ["id", "user_id", "phone", "address", "total", "created_at", "items"]