from typing import List
from .models import Article, ProductRequirement, Product
from .business_logic.data_transfer_objects import CreateProductDTO, CreateProductRequirementDTO, ArticleDTO

class ArticleRepository:
    def partition_ids_by_existence(self, article_ids: List[int]):
        queryset_existing_ids = Article.objects.filter(id__in=article_ids).values('id')
        existing_ids = list(map(lambda qs: qs['id'], queryset_existing_ids))
        no_existing_ids = list(filter(lambda id: id not in existing_ids, article_ids))

        return (existing_ids, no_existing_ids)

    def save_articles(self, articles: List[ArticleDTO]):
        article_ids = map(lambda article: article.id, articles)
        (existing_ids, no_existing_ids) = self.partition_ids_by_existence(article_ids)
        existing_articles = filter(lambda article: article.id in existing_ids, articles)
        not_existing_articles = filter(lambda article: article.id in no_existing_ids, articles)

        Article.objects.bulk_update(existing_articles, fields=['name', 'stock'])
        Article.objects.bulk_create(not_existing_articles)


class ProductRepository:
    def partition_names_by_existence(self, product_names: List[str]):
        queryset_existing_names = Product.objects.filter(name__in=product_names).values('name')
        existing_names = list(map(lambda qs: qs['name'], queryset_existing_names))
        no_existing_names = list(filter(lambda name: name not in existing_names), product_names)

        return (existing_names, no_existing_names)

    def create_products(self, products: List[CreateProductDTO]):
        product_models = map(lambda p: Product(name=p.name), products)
        created_product_models = Product.objects.bulk_create(product_models)

        requirement_models = map(
          lambda created_product, product: self._map_requirement(product.requirements, created_product),
          zip(created_product_models, products)
        )

        ProductRequirement.objects.bulk_create(flat_list(requirement_models))

    def _map_requirement(self, product_requirements: List[CreateProductRequirementDTO], created_product: Product):
        return map(
          lambda requirement: ProductRequirement(**requirement, product=created_product),
          product_requirements
        )


def flat_list(list_groups):
    return [item for group in list_groups for item in group]
