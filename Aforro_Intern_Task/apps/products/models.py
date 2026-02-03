from django.db import models

class Category(models.Model): # [cite: 10]
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model): # [cite: 12]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    class Meta:
        indexes = [models.Index(fields=['title'])] # For search optimization