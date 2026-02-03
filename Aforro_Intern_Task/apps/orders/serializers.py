from django.db import transaction
from rest_framework import serializers
from .models import Order, OrderItem
from apps.stores.models import Inventory
from .tasks import send_order_confirmation

# 1. Serializer for individual items in the response
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'quantity_requested']

# 2. Serializer for listing orders (GET)
class OrderListSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'total_items', 'order_items']

    def get_total_items(self, obj):
        return obj.items.count()

# 3. Serializer for creating orders (POST)
class OrderCreateSerializer(serializers.ModelSerializer):
    # INPUT: detailed list of items (Write Only)
    items = serializers.ListField(child=serializers.DictField(), write_only=True)
    
    # OUTPUT: formatted nested objects (Read Only)
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'store', 'status', 'items', 'order_items']
        read_only_fields = ['status', 'id']

    def create(self, validated_data):
        store = validated_data['store']
        items_data = validated_data['items']

        with transaction.atomic():
            order = Order.objects.create(store=store, status='PENDING')
            
            insufficient_stock = False
            
            # Lock rows and validate
            for item in items_data:
                product_id = item['product_id']
                qty_requested = item['quantity']

                try:
                    inventory = Inventory.objects.select_for_update().get(
                        store=store, 
                        product_id=product_id
                    )
                    if inventory.quantity < qty_requested:
                        insufficient_stock = True
                except Inventory.DoesNotExist:
                    insufficient_stock = True
                
                if insufficient_stock:
                    break
            
            # Failure Case
            if insufficient_stock:
                order.status = 'REJECTED'
                order.save()
                return order

            # Success Case: Deduct and Create Items
            for item in items_data:
                inventory = Inventory.objects.get(store=store, product_id=item['product_id'])
                inventory.quantity -= item['quantity']
                inventory.save()
                
                OrderItem.objects.create(
                    order=order,
                    product_id=item['product_id'],
                    quantity_requested=item['quantity']
                )

            order.status = 'CONFIRMED'
            order.save()
            
            # --- ASYNC TASK TRIGGER ---
            # Trigger the Celery task to send confirmation email asynchronously
            send_order_confirmation.delay(order.id)
            
            return order