from dataclasses import dataclass
from typing import List

@dataclass
class CreateProductRequirementDTO:
    quantity: int
    article_id: int

@dataclass
class CreateProductDTO:
    name: str
    requirements: List[CreateProductRequirementDTO]

@dataclass
class ArticleDTO:
    id: int
    name: str
    stock: int

@dataclass
class ProductRequirementDTO:
    quantity: int
    article: ArticleDTO

@dataclass
class ProductDTO:
    id: int
    name: str
    requirements: List[ProductRequirementDTO]

@dataclass
class ProductAvailability:
    id: int
    name: str
    availability: int
