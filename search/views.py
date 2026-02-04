from django.db.models import Q, F, Value, IntegerField, Case, When
from django.db.models.functions import Coalesce

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from products.models import Product
from stores.models import Inventory
from .serializers import ProductSearchSerializer


class ProductSearchAPIView(ListAPIView):
    serializer_class = ProductSearchSerializer

    def get_queryset(self):

        qs = (
            Product.objects
            .select_related("category")
            .all()
        )


        q = self.request.query_params.get("q")
        category = self.request.query_params.get("category")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        store_id = self.request.query_params.get("store_id")
        in_stock = self.request.query_params.get("in_stock")
        sort = self.request.query_params.get("sort")

       
       
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(category__name__icontains=q)
            )



        if category:
            qs = qs.filter(category__name__iexact=category)

        if min_price:
            qs = qs.filter(price__gte=min_price)

        if max_price:
            qs = qs.filter(price__lte=max_price)



        if store_id:
            qs = qs.annotate(
                inventory_quantity=Coalesce(
                    Inventory.objects.filter(
                        store_id=store_id,
                        product_id=F("id")
                    ).values("quantity")[:1],
                    Value(0),
                    output_field=IntegerField()
                )
            )

            if in_stock == "true":
                qs = qs.filter(inventory_quantity__gt=0)



        if sort == "price":
            qs = qs.order_by("price")

        elif sort == "-price":
            qs = qs.order_by("-price")

        elif sort == "newest":
            qs = qs.order_by("-created_at")

        elif sort == "relevance" and q:
            qs = qs.annotate(
                relevance=Case(
                    When(title__icontains=q, then=Value(3)),
                    When(category__name__icontains=q, then=Value(2)),
                    When(description__icontains=q, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by("-relevance")

        return qs

class ProductSuggestAPIView(APIView):

    def get(self, request):

        q = request.query_params.get("q", "").strip()

        if len(q) < 3:
            return Response(
                {"detail": "At least 3 characters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        prefix_qs = (
            Product.objects
            .filter(title__istartswith=q)
            .order_by("title")
            .values_list("title", flat=True)[:10]
        )

        remaining = 10 - len(prefix_qs)

        suggestions = list(prefix_qs)

        if remaining > 0:
            general_qs = (
                Product.objects
                .filter(title__icontains=q)
                .exclude(title__istartswith=q)
                .order_by("title")
                .values_list("title", flat=True)[:remaining]
            )

            suggestions.extend(list(general_qs))

        return Response(
            {
                "results": suggestions
            }
        )
