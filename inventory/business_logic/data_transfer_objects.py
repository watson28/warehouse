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
