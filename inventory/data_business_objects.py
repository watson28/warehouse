from dataclasses import dataclass
from typing import List

@dataclass
class CreateProductRequirementDBO:
    quantity: int
    article_id: int

@dataclass
class CreateProductDBO:
    name: str
    requirements: List[CreateProductRequirementDBO]

@dataclass
class ArticleDBO:
    id: int
    name: str
    stock: int

@dataclass
class ProductRequirementDBO:
    quantity: int
    article: ArticleDBO

@dataclass
class ProductDBO:
    id: int
    name: str
    requirements: List[ProductRequirementDBO]

@dataclass
class ProductAvailabilityDBO:
    id: int
    name: str
    availability: int
