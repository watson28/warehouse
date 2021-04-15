from typing import List
from django.db import transaction
from ..repositories import ArticleRepository, ProductRepository
from .data_transfer_objects import CreateProductDTO, ArticleDTO, ProductAvailability, ProductRequirementDTO

class ArticleBusiness:
    def __init__(self):
        self._article_repository = ArticleRepository()

    def save_articles(self, articles: List[ArticleDTO]):
        self._article_repository.save_articles(articles)


class ProductBusiness:
    def __init__(self):
        self._article_repository = ArticleRepository()
        self._product_repository = ProductRepository()

    def save_products(self, products: List[CreateProductDTO]):
        self.validate_product_names_not_exist(products)
        self.validate_product_requirement_articles_exist(products)
        with transaction.atomic():
            self._product_repository.create_products(products)

    def get_products_availability(self) -> List[ProductAvailability]:
        products = self._product_repository.get_products_with_requirement_details()
        return [
            ProductAvailability(
                id=product.id,
                name=product.name,
                availability=self._get_product_availability(product.requirements)
            )
            for product in products
        ]

    def _get_product_availability(self, requirements: List[ProductRequirementDTO]) -> int:
        return min([req.article.stock // req.quantity for req in requirements])

    def validate_product_requirement_articles_exist(self, products: List[CreateProductDTO]):
        product_requirements = flat_list([product.requirements for product in products])
        article_ids = set(map(lambda requirement: requirement.article_id, product_requirements))
        (_, no_existing_ids) = self._article_repository.partition_ids_by_existence(article_ids)

        if len(no_existing_ids) > 0:
            raise ArticleNotExistException(no_existing_ids)

    def validate_product_names_not_exist(self, products):
        product_names = map(lambda product: product.name, products)
        (existing_names, _) = self._product_repository.partition_names_by_existence(product_names)

        if len(existing_names) > 0:
            raise ProductAlreadyExistException(*existing_names)


class ProductAlreadyExistException(Exception):
    def __init__(self, *existing_product_names):
        self.existing_product_names = existing_product_names
        joined_names = ','.join(self.existing_product_names)
        super().__init__(f'Products already exist with names: {joined_names}')

class ArticleNotExistException(Exception):
    def __init__(self, *no_existing_article_ids):
        self.no_existing_article_ids = no_existing_article_ids
        joined_ids = ','.join([str(id) for id in self.no_existing_article_ids])
        super().__init__(f'Articles dont exist with ids: {joined_ids}')


def flat_list(list_groups):
    return [item for group in list_groups for item in group]
