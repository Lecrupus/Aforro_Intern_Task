from django.db import models

class Store(models.Model): # [cite: 17]
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

class Inventory(models.Model): # [cite: 20]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        # Constraint: A store must have at most one inventory row per product [cite: 24]
        unique_together = ('store', 'product')