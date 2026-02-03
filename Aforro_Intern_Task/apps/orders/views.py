from rest_framework import generics
from .models import Order
from .serializers import OrderCreateSerializer, OrderListSerializer # Assume ListSerializer exists

class OrderCreateView(generics.CreateAPIView): # [cite: 34]
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

class OrderListView(generics.ListAPIView): # [cite: 50]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        # Optimization: Prevent N+1 issues [cite: 56]
        return Order.objects.filter(store_id=store_id)\
            .prefetch_related('items__product')\
            .order_by('-created_at')