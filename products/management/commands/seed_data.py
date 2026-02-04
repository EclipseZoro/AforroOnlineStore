import random

from django.core.management.base import BaseCommand
from django.db import transaction

from faker import Faker

from products.models import Category, Product
from stores.models import Store, Inventory
from orders.models import Order, OrderItem

class Command(BaseCommand):
    help = "Seed database with categories, products, stores and inventory"
    

    def handle(self, *args, **options):

        fake = Faker()

        with transaction.atomic():
            Inventory.objects.all().delete()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            Store.objects.all().delete()

            self.stdout.write("Creating categories...")

            categories = []
            for _ in range(10):
                categories.append(
                    Category(
                        name=fake.unique.word().title()
                    )
                )

            Category.objects.bulk_create(categories)

            categories = list(Category.objects.all())


            self.stdout.write("Creating products...")

            products = []

            for _ in range(1000):
                products.append(
                    Product(
                        title=fake.unique.sentence(nb_words=3),
                        description=fake.text(max_nb_chars=200),
                        price=round(random.uniform(10, 1000), 2),
                        category=random.choice(categories)
                    )
                )

            Product.objects.bulk_create(products)

            products = list(Product.objects.all())


            self.stdout.write("Creating stores...")

            stores = []

            for _ in range(20):
                stores.append(
                    Store(
                        name=fake.company(),
                        location=fake.city()
                    )
                )

            Store.objects.bulk_create(stores)

            stores = list(Store.objects.all())


            self.stdout.write("Creating inventory...")

            inventory_rows = []

            for store in stores:
                store_products = random.sample(products, 300)

                for product in store_products:
                    inventory_rows.append(
                        Inventory(
                            store=store,
                            product=product,
                            quantity=random.randint(0, 200)
                        )
                    )

            Inventory.objects.bulk_create(inventory_rows)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
