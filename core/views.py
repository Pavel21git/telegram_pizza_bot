from rest_framework import viewsets
from .models import Pizza, Order
from .serializers import PizzaSerializer, OrderSerializer

class PizzaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all().order_by("-id")
    serializer_class = OrderSerializer