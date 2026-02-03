from django.contrib import admin
from django.urls import path
from apps.orders.views import OrderCreateView, OrderListView
from apps.search.views import ProductSearchView, AutocompleteView
from apps.stores.views import InventoryListView  # <-- Add this import

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Order Endpoints
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    path('stores/<int:store_id>/orders/', OrderListView.as_view(), name='store-orders'),

    # Inventory Endpoint (Requirement 1.4)
    path('stores/<int:store_id>/inventory/', InventoryListView.as_view(), name='store-inventory'), # <-- Add this line
    
    # Search Endpoints
    path('api/search/products/', ProductSearchView.as_view(), name='product-search'),
    path('api/search/suggest/', AutocompleteView.as_view(), name='product-suggest'),
]