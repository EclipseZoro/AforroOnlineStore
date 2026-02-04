from rest_framework import searializers
from .models import Order, OrderItem

class OrderItemCreateSerializer(searializers.ModelSerializer):
    product_id = searializers.IntergerField()
    quantity_requested = searializers.IntegerField(min_value=1)

class OrderCreateSerializer(searializers.ModelSerializer):
    store_id = searializers.IntergerField()
    items = OrderItemCreateSerializer(many=True)

    def validate_item(self, value):
        product_ids = [item['product_id'] for item in value]

        if len(product_ids) != len(set(product_ids)):
            raise searializers.ValidationError("Duplicate products are not allowed.")
        
        return value

class OrderItemResponseSerailizer(searializers.ModelSerializer):
    class Meta:
        model = OrderItem
        firleds = ('product_id', 'quantity_requested')

class OrderResponseSerializer(searializers.ModelSerializer):
    items = OrderItemResponseSerailizer(many=True)
    class Meta:
        model = Order
        fields = ('id', 'status', 'created_at', 'items')
    



