from rest_framework import generics
from .models import Inventory
from .serializers import InventorySerializer

class InventoryListView(generics.ListAPIView):
    serializer_class = InventorySerializer

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        
        # Requirement 1.4: 
        # 1. Filter by Store
        # 2. Sort alphabetically by product title
        # 3. Optimization: Use select_related to fetch Product + Category in 1 query
        return Inventory.objects.filter(store_id=store_id)\
            .select_related('product', 'product__category')\
            .order_by('product__title')