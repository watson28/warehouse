from django.db import models
from django.core.validators import MinValueValidator

class Article(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=128, null=False, unique=True)
    stock = models.PositiveIntegerField(null=False)

class Product(models.Model):
    name = models.CharField(max_length=128, null=False, unique=True)

class ProductRequirement(models.Model):
    article = models.ForeignKey(Article, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='requirements')
    quantity = models.PositiveIntegerField(null=False, validators=[MinValueValidator(1)])
