from typing import List
from .data_business_objects import CreateProductDTO, CreateProductRequirementDTO, ArticleDTO

class InvalidDataUploadError(Exception):
    def __init__(self, *errors):
        self.errors = errors
        super().__init__('\n'.join(self.errors))

class InvalidUploadAttributeError(InvalidDataUploadError):
    def __init__(self, context, attribute, error):
        super().__init__(f'attribute {context}.{attribute}: {error}')


class UploadParser:
    def parse_field(self, obj, field_name, obj_context):
        if field_name not in obj:
            raise InvalidUploadAttributeError(obj_context, field_name, 'not found')

        return obj[field_name]

    def parse_numeric_field(self, obj, field_name, obj_context):
        value = self.parse_field(obj, field_name, obj_context)
        try:
            return int(value)
        except ValueError as exception:
            raise InvalidUploadAttributeError(obj_context, field_name, 'expected number') from exception

    def parse_string_field(self, obj, field_name, obj_context):
        value = self.parse_field(obj, field_name, obj_context)
        if not isinstance(value, str):
            raise InvalidDataUploadError(f'attribute {obj_context}.{field_name}: expected string')

        return value.strip()

    def parse_list_field(self, obj, field_name, obj_context):
        value = self.parse_field(obj, field_name, obj_context)
        if not isinstance(value, list):
            raise InvalidUploadAttributeError(obj_context, field_name, 'expected list')

        return value

    def parse_list_items(self, obj_list, parser_fn, obj_context):
        parsed_items = []
        format_errors = []
        for index, item in enumerate(obj_list):
            try:
                parsed_items.append(parser_fn(item, f'{obj_context}[{index}]'))
            except InvalidDataUploadError as exception:
                format_errors.append(str(exception))

            if len(format_errors) > 0:
                raise InvalidDataUploadError(*format_errors)

        return parsed_items


class ArticleUploadParser:
    def __init__(self):
        self._parser = UploadParser()

    def parse(self, data: dict) -> List[ArticleDTO]:
        articles = self._parser.parse_list_field(data, 'inventory', 'root')
        return self._parser.parse_list_items(articles, self._parse_article, 'inventory')

    def _parse_article(self, article, obj_context) -> ArticleDTO:
        article_id = self._parser.parse_numeric_field(article, 'art_id', obj_context)
        name = self._parser.parse_string_field(article, 'name', obj_context)
        stock = self._parser.parse_numeric_field(article, 'stock', obj_context)

        return ArticleDTO(id=article_id, name=name, stock=stock)


class ProductUploadParser:
    def __init__(self):
        self._parser = UploadParser()

    def parse(self, data: dict) -> List[CreateProductDTO]:
        products = self._parser.parse_list_field(data, 'products', 'root')
        return self._parser.parse_list_items(products, self._parse_product, 'products')

    def _parse_product(self, item, obj_context) -> CreateProductDTO:
        name = self._parser.parse_string_field(item, 'name', obj_context)
        requirement_items = self._parser.parse_list_field(item, 'contain_articles', obj_context)
        requirements = self._parser.parse_list_items(requirement_items , self._parse_product_requirement, obj_context)

        return CreateProductDTO(name=name, requirements=requirements)

    def _parse_product_requirement(self, obj, obj_context) -> CreateProductRequirementDTO:
        article_id = self._parser.parse_numeric_field(obj, 'art_id', obj_context)
        quantity = self._parser.parse_numeric_field(obj, 'amount_of', obj_context)

        if quantity <= 0:
            raise InvalidDataUploadError(obj_context, 'quantity', 'expected value greater than 0')

        return CreateProductRequirementDTO(article_id=article_id, quantity=quantity)
        