from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from products.models import Category, Product
from stores.models import Store, Inventory
from orders.models import Order


class AssignmentFlowTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(name="Food")

        self.product1 = Product.objects.create(
            title="Milk",
            price=50,
            category=self.category
        )

        self.product2 = Product.objects.create(
            title="Bread",
            price=30,
            category=self.category
        )

        self.store = Store.objects.create(
            name="Main Store",
            location="City"
        )

        Inventory.objects.create(
            store=self.store,
            product=self.product1,
            quantity=10
        )

        Inventory.objects.create(
            store=self.store,
            product=self.product2,
            quantity=5
        )


    def test_order_creation_confirmed_and_stock_deducted(self):

        payload = {
            "store_id": self.store.id,
            "items": [
                {"product_id": self.product1.id, "quantity_requested": 3},
                {"product_id": self.product2.id, "quantity_requested": 2},
            ]
        }

        response = self.client.post("/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)

        order = Order.objects.first()
        self.assertEqual(order.status, Order.Status.CONFIRMED)

        inv1 = Inventory.objects.get(store=self.store, product=self.product1)
        inv2 = Inventory.objects.get(store=self.store, product=self.product2)

        self.assertEqual(inv1.quantity, 7)
        self.assertEqual(inv2.quantity, 3)


    def test_order_creation_rejected_when_insufficient_stock(self):

        payload = {
            "store_id": self.store.id,
            "items": [
                {"product_id": self.product1.id, "quantity_requested": 50}
            ]
        }

        response = self.client.post("/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)

        order = Order.objects.first()
        self.assertEqual(order.status, Order.Status.REJECTED)

        inv = Inventory.objects.get(store=self.store, product=self.product1)
        self.assertEqual(inv.quantity, 10)

    def test_inventory_unique_per_store_product(self):

        with self.assertRaises(Exception):
            Inventory.objects.create(
                store=self.store,
                product=self.product1,
                quantity=1
            )


    def test_store_orders_list_returns_total_items(self):

        payload = {
            "store_id": self.store.id,
            "items": [
                {"product_id": self.product1.id, "quantity_requested": 2},
                {"product_id": self.product2.id, "quantity_requested": 3},
            ]
        }

        self.client.post("/orders/", payload, format="json")

        response = self.client.get(
            f"/stores/{self.store.id}/orders/"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]["total_items"], 5)


    def test_autocomplete_requires_minimum_three_characters(self):

        response = self.client.get(
            "/api/search/suggest/?q=mi"
        )

        self.assertEqual(response.status_code, 400)
