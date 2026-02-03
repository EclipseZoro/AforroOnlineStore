from django.db import models

class Store(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    store = models.ForeignKey(Store,on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.product.title} in {self.store.name}"
    

