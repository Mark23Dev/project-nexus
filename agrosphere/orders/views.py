from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Order
from .serializers import OrderSerializer

class OrderListCreateView(generics.ListCreateAPIView):
    """
    List orders (admin: all orders; users: own orders) and create orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items__product', 'items')
        return Order.objects.filter(user=user).prefetch_related('items__product', 'items')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an order with permission checks.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items__product', 'items')
        return Order.objects.filter(user=user).prefetch_related('items__product', 'items')

    def perform_update(self, serializer):
        order = self.get_object()
        if self.request.user != order.user and not self.request.user.is_staff:
            raise PermissionDenied("You cannot modify this order.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user and not self.request.user.is_staff:
            raise PermissionDenied("You cannot delete this order.")
        if instance.status != 'pending':
            raise PermissionDenied("Only pending orders can be deleted.")
        instance.delete()
