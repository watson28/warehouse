from django.db import models

class Article(models.Model):
  id = models.BigIntegerField(primary_key=True)
  name = models.CharField(max_length=128, null=False)
  stock = models.PositiveIntegerField(null=False)

class Product(models.Model):
  name = models.CharField(max_length=128, null=False)

class ProductRequirement(models.Model):
  article = models.ForeignKey(Article, on_delete=models.PROTECT)
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(null=False)
