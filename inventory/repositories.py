from typing import List
from dataclasses import asdict
from django.db import transaction

from .models import Article, ProductRequirement, Product
from .business_logic.data_transfer_objects import (
    CreateProductDTO,
    CreateProductRequirementDTO,
    ArticleDTO,
    ProductDTO,
    ProductRequirementDTO
)

class ArticleRepository:
    def partition_ids_by_existence(self, article_ids: List[int]):
        queryset_existing_ids = Article.objects.filter(id__in=article_ids).values('id')
        existing_ids = list(map(lambda qs: qs['id'], queryset_existing_ids))
        no_existing_ids = list(filter(lambda id: id not in existing_ids, article_ids))

        return (existing_ids, no_existing_ids)

    def save_articles(self, articles: List[ArticleDTO]):
        article_models = list(map(lambda article: Article(**asdict(article)),articles))
        article_ids = list(map(lambda article: article.id, articles))
        (existing_ids, no_existing_ids) = self.partition_ids_by_existence(article_ids)
        existing_articles = list(filter(lambda article: article.id in existing_ids, article_models))
        not_existing_articles = list(filter(lambda article: article.id in no_existing_ids, article_models))

        with transaction.atomic():
            Article.objects.bulk_update(existing_articles, fields=['name', 'stock'])
            Article.objects.bulk_create(not_existing_articles)

    def update_articles_stock(self, new_article_stocks: dict):
        articles = [Article(id=id, stock=stock) for (id, stock) in new_article_stocks.items()]
        Article.objects.bulk_update(articles, fields=['stock'])


class ProductRepository:
    def partition_names_by_existence(self, product_names: List[str]):
        queryset_existing_names = Product.objects.filter(name__in=product_names).values('name')
        existing_names = list(map(lambda qs: qs['name'], queryset_existing_names))
        no_existing_names = list(filter(lambda name: name not in existing_names, product_names))

        return (existing_names, no_existing_names)

    def create_products(self, products: List[CreateProductDTO]):
        product_models = map(lambda p: Product(name=p.name), products)

        with transaction.atomic():
            created_product_models = Product.objects.bulk_create(product_models)
            requirement_models = list(
                map(
                    lambda zip_tuple: self._map_requirement(zip_tuple[0].requirements, zip_tuple[1]),
                    zip(products, created_product_models)
                )
            )
            ProductRequirement.objects.bulk_create(flat_list(requirement_models))

    def get_products_with_requirement_details(self) -> List[ProductDTO]:
        #TODO: implement pagination to reduce the size of the information in memory.
        #fetch products with their requirements and articles in three queries.
        products = Product.objects.all() \
            .prefetch_related('requirements') \
            .prefetch_related('requirements__article')

        return list(map(self._product_with_requirements_to_dto, products))

    def get_product_with_requirement_details(self, product_id: int):
        product = Product.objects \
            .prefetch_related('requirements') \
            .prefetch_related('requirements__article') \
            .get(id=product_id)

        return self._product_with_requirements_to_dto(product)

    def _product_with_requirements_to_dto(self, product: Product):
        requirements_to_dto = lambda requirement: ProductRequirementDTO(
            quantity=requirement.quantity,
            article = Article(
                id=requirement.article.id,
                name=requirement.article.name,
                stock=requirement.article.stock
            )
        )
        return ProductDTO(
            id=product.id,
            name=product.name,
            requirements=list(map(requirements_to_dto, product.requirements.all()))
        )

    def _map_requirement(self, product_requirements: List[CreateProductRequirementDTO], created_product: Product):
        return map(
          lambda requirement: ProductRequirement(**asdict(requirement), product=created_product),
          product_requirements
        )


def flat_list(list_groups):
    return [item for group in list_groups for item in group]
