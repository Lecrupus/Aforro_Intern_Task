from django.db.models import Q, Subquery, OuterRef, IntegerField, Value, Case, When
from django.db.models.functions import Coalesce
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.pagination import PageNumberPagination
from apps.products.models import Product
from apps.stores.models import Inventory
from .serializers import ProductSearchSerializer

# Standard Pagination Metadata
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# 1. Product Search API (Filters, Sorting, & Store Stock)
class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSearchSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Start with all products
        queryset = Product.objects.all().select_related('category')
        
        # --- KEYWORD SEARCH (Title, Description, Category) ---
        q = self.request.query_params.get('q', None)
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(category__name__icontains=q)
            )

        # --- ANNOTATION: Inventory for specific store ---
        # "If store_id is provided, include the product’s inventory quantity"
        store_id = self.request.query_params.get('store_id', None)
        if store_id:
            # Subquery to fetch quantity from Inventory table matching Product + Store
            stock_subquery = Inventory.objects.filter(
                store_id=store_id, 
                product=OuterRef('pk')
            ).values('quantity')[:1]

            queryset = queryset.annotate(
                store_quantity=Coalesce(Subquery(stock_subquery), Value(0), output_field=IntegerField())
            )
            
            # Filter: in_stock (Only valid if store context is known)
            in_stock = self.request.query_params.get('in_stock', None)
            if in_stock == 'true':
                queryset = queryset.filter(store_quantity__gt=0)

        # --- FILTERS ---
        # Category Filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name__iexact=category)

        # Price Range Filter
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # --- SORTING ---
        sort_by = self.request.query_params.get('sort', 'relevance')
        
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-id') 
        else:
            queryset = queryset.order_by('-id') # Default

        return queryset

# 2. Autocomplete API (Optimized for Speed)
class AutocompleteView(APIView):
    # Requirement 2.1: Rate Limit specific to this endpoint (20/min)
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'suggest'

    def get(self, request):
        query = request.query_params.get('q', '')

        # Rule 1: Minimum 3 characters required
        if len(query) < 3:
            return Response([])

        # Rule 2 & 3: Prefix matches before general matches
        # Logic: 
        # 1. Filter all items containing the query
        # 2. Score '1' if starts with query, '0' otherwise
        # 3. Sort by score (desc) -> Prefix matches float to top
        results = Product.objects.filter(title__icontains=query).annotate(
            is_prefix=Case(
                When(title__istartswith=query, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('-is_prefix', 'title').values_list('title', flat=True)[:10]

        return Response(list(results))