from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView

from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderResponseSerializer, StoreOrderListSerializer

from stores.models import Store, Inventory
from products.models import Product


class OrderCreateAPIView(APIView):

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store_id = serializer.validated_data["store_id"]
        items = serializer.validated_data["items"]

        store = get_object_or_404(Store, id=store_id)

        product_ids = [item["product_id"] for item in items]

        products = Product.objects.filter(id__in=product_ids)

        if products.count() != len(product_ids):
            return Response(
                {"detail": "One or more products do not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        

        

        with transaction.atomic():
            inventories = Inventory.objects.select_for_update().filter(
            store=store,
            product_id__in=product_ids
        )
            inventory_map = {
            inv.product_id: inv for inv in inventories
        }

            insufficient = False

            for item in items:
                inv = inventory_map.get(item["product_id"])

                if not inv:
                    insufficient = True
                    break

                if inv.quantity < item["quantity_requested"]:
                    insufficient = True
                    break

            if insufficient:
                order = Order.objects.create(
                    store=store,
                    status=Order.Status.REJECTED
                )

                OrderItem.objects.bulk_create([
                    OrderItem(
                        order=order,
                        product_id=item["product_id"],
                        quantity_requested=item["quantity_requested"]
                    )
                    for item in items
                ])

                return Response(
                    OrderResponseSerializer(order).data,
                    status=status.HTTP_201_CREATED
                )

            order = Order.objects.create(
                store=store,
                status=Order.Status.CONFIRMED
            )

            order_items = []
            for item in items:
                order_items.append(
                    OrderItem(
                        order=order,
                        product_id=item["product_id"],
                        quantity_requested=item["quantity_requested"]
                    )
                )

            OrderItem.objects.bulk_create(order_items)

            for item in items:
                inv = inventory_map[item["product_id"]]
                inv.quantity -= item["quantity_requested"]
                inv.save(update_fields=["quantity"])

            return Response(
                OrderResponseSerializer(order).data,
                status=status.HTTP_201_CREATED
            )

class StoreOrderListAPIView(ListAPIView):
    serializer_class = StoreOrderListSerializer

    def get_queryset(self):
        store_id = self.kwargs["store_id"]

        return (
            Order.objects
            .filter(store_id=store_id)
            .annotate(
                total_items=Sum("items__quantity_requested")
            )
            .order_by("-created_at")
        )
