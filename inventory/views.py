import json
from dataclasses import asdict
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status

from .upload_parsers import (
    ProductUploadParser,
    ArticleUploadParser,
    InvalidDataUploadError
)
from .business_logic import (
    ArticleBusiness,
    ProductBusiness,
    BusinessValidationError
)

class JSONFileParser(FileUploadParser):
    media_type = 'application/json'


class APIVieWithErrorHandling(APIView):
    def handle_exception(self, exc):
        if isinstance(exc, BusinessValidationError):
            return Response({ 'errors': [str(exc)] }, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(exc, InvalidDataUploadError):
            return Response({ 'errors': exc.errors }, status=status.HTTP_400_BAD_REQUEST)

        return super().handle_exception(exc)


def read_upload_file_content(request: HttpRequest):
    file = request.data.get('file')
    if file is None:
        raise InvalidDataUploadError('expected key "file" in payload')
    try:
        return json.load(file)
    except json.decoder.JSONDecodeError as exception:
        raise InvalidDataUploadError(f'Invalid JSON structure. {str(exception)}') from exception


class UploadArticlesView(APIVieWithErrorHandling):
    parser_classes = [JSONFileParser]

    def __init__(self, **kwargs):
        self._article_upload_parser = ArticleUploadParser()
        self._article_business = ArticleBusiness()
        super().__init__(**kwargs)

    def post(self, request):
        data = read_upload_file_content(request)
        articles = self._article_upload_parser.parse(data)
        self._article_business.save_articles(articles)

        return Response(status=status.HTTP_201_CREATED)


class UploadProductsView(APIVieWithErrorHandling):
    parser_classes = [JSONFileParser]

    def __init__(self, **kwargs):
        self._product_upload_parser = ProductUploadParser()
        self._product_business = ProductBusiness()
        super().__init__(**kwargs)

    def post(self, request):
        data = read_upload_file_content(request)
        products = self._product_upload_parser.parse(data)
        self._product_business.save_products(products)

        return Response(status=status.HTTP_201_CREATED)


class ProductsAvailabilityView(APIVieWithErrorHandling):
    def __init__(self, **kwargs):
        self._product_business = ProductBusiness()
        super().__init__(**kwargs)

    def get(self,request):
        products_availability = self._product_business.get_products_availability()

        return Response(
            [asdict(item) for item in products_availability],
            status=status.HTTP_200_OK
        )


class SellProductView(APIVieWithErrorHandling):
    def __init__(self, **kwargs):
        self._product_business = ProductBusiness()
        super().__init__(**kwargs)

    def post(self, request, product_id):
        self._product_business.sell_product(product_id)

        return Response(status=status.HTTP_200_OK)
