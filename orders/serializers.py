from rest_framework import serializers
from .models import Order, OrderItem
from django.db.models import Sum

class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity_requested = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    items = OrderItemCreateSerializer(many=True)

    def validate_item(self, value):
        product_ids = [item['product_id'] for item in value]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate products are not allowed.")
        
        return value

class OrderItemResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product_id', 'quantity_requested')

class OrderResponseSerializer(serializers.ModelSerializer):
    items = OrderItemResponseSerializer(many=True)
    class Meta:
        model = Order
        fields = ('id', 'status', 'created_at', 'items')
    
class StoreOrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.IntegerField()
    class Meta:
        model = Order
        fields = ('id', 'status', 'created_at', 'total_items')




