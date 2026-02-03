from rest_framework import serializers
from apps.products.models import Product

class ProductSearchSerializer(serializers.ModelSerializer):
    # This field comes from the 'annotate' in the View
    store_quantity = serializers.IntegerField(read_only=True, required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category_name', 'store_quantity']