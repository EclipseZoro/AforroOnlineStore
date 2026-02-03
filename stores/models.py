from django.db import models
from products.models import Product
class Store(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventories')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    quantity = models.PositiveIntegerField()
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'product'], name='unique_inventory_per_store_product')
        ]
    def __str__(self):
        return f"{self.store} - {self.product}"
    

