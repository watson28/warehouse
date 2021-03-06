from typing import List, Iterable, Any
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .repositories import ArticleRepository, ProductRepository
from .data_business_objects import (
    CreateProductDBO,
    ArticleDBO,
    ProductAvailabilityDBO,
    ProductDBO,
    ProductRequirementDBO
)

class ArticleBusiness:
    def __init__(self) -> None:
        self._article_repository = ArticleRepository()

    def save_articles(self, articles: List[ArticleDBO]) -> None:
        self._article_repository.save_articles(articles)


class ProductBusiness:
    def __init__(self) -> None:
        self._article_repository = ArticleRepository()
        self._product_repository = ProductRepository()

    def save_products(self, products: List[CreateProductDBO]) -> None:
        self.validate_product_names_not_exist(products)
        self.validate_product_requirement_articles_exist(products)
        with transaction.atomic():
            self._product_repository.create_products(products)

    def get_products_availability(self) -> List[ProductAvailabilityDBO]:
        products = self._product_repository.get_products_with_requirement_details()
        return [
            ProductAvailabilityDBO(
                id=product.id,
                name=product.name,
                availability=self._get_product_availability(product.requirements)
            )
            for product in products
        ]

    def sell_product(self, product_id: int) -> None:
        try:
            product = self._product_repository.get_product_with_requirement_details(product_id)
            self.validate_product_availability(product)
            self._reduce_article_stocks_from_requirements(product.requirements)
        except ObjectDoesNotExist as exception:
            raise ProductDoesNotExistError(product_id) from exception

    def validate_product_availability(self, product: ProductDBO) -> None:
        availability = self._get_product_availability(product.requirements)
        if availability == 0:
            raise ProductNotAvailableError(product.id)

    def validate_product_requirement_articles_exist(self, products: List[CreateProductDBO]) -> None:
        product_requirements = flat_list([product.requirements for product in products])
        article_ids = set(map(lambda requirement: requirement.article_id, product_requirements))
        (_, no_existing_ids) = self._article_repository.partition_ids_by_existence(article_ids)

        if len(no_existing_ids) > 0:
            raise ArticleDoesNotExistError(*no_existing_ids)

    def validate_product_names_not_exist(self, products: Iterable[CreateProductDBO]) -> None:
        product_names = map(lambda product: product.name, products)
        (existing_names, _) = self._product_repository.partition_names_by_existence(product_names)

        if len(existing_names) > 0:
            raise ProductAlreadyExistError(*existing_names)

    def _get_product_availability(self, requirements: List[ProductRequirementDBO]) -> int:
        return min([req.article.stock // req.quantity for req in requirements])

    def _reduce_article_stocks_from_requirements(self, requirements: List[ProductRequirementDBO]) -> None:
        new_product_articles_stock = {
            requirement.article.id: requirement.article.stock - requirement.quantity
            for requirement in requirements
        }
        self._article_repository.update_articles_stock(new_product_articles_stock)

class BusinessValidationError(Exception):
    pass

class ProductAlreadyExistError(BusinessValidationError):
    def __init__(self, *existing_product_names: str) -> None:
        self.existing_product_names = existing_product_names
        joined_names = ','.join(self.existing_product_names)
        super().__init__(f'Products already exist with names: {joined_names}')

class ArticleDoesNotExistError(BusinessValidationError):
    def __init__(self, *no_existing_article_ids: int) -> None:
        self.no_existing_article_ids = no_existing_article_ids
        joined_ids = ','.join([str(id) for id in self.no_existing_article_ids])
        super().__init__(f'Articles dont exist with ids: {joined_ids}')

class ProductNotAvailableError(BusinessValidationError):
    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(f'Product quantity is zero with id={product_id}')

class ProductDoesNotExistError(BusinessValidationError):
    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(f'Product does not exist with id={product_id}')


def flat_list(list_groups: Iterable[Iterable[Any]]) -> Iterable[Any]:
    return [item for group in list_groups for item in group]
