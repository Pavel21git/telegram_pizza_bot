from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PizzaViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"pizzas", PizzaViewSet, basename="pizza")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]