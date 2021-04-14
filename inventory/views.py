import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status

from .business_logic.business_logic import ArticleBusiness, ProductBusiness
from .business_logic.upload_parsers import ProductUploadParser, ArticleUploadParser, InvalidDataUploadException

class JSONFileParser(FileUploadParser):
    media_type = 'application/json'

class UploadArticlesView(APIView):
    parser_classes = [JSONFileParser]

    def __init__(self, **kwargs):
        self._article_upload_parser = ArticleUploadParser()
        self._article_business = ArticleBusiness()
        super().__init__(**kwargs)

    def post(self, request):
        try:
            data = json.load(request.data['file'])
            articles = self._article_upload_parser.parse(data)
            self._article_business.save_articles(articles)
        except InvalidDataUploadException as exception:
            return Response({ 'errors': exception.errors }, status=status.HTTP_400_BAD_REQUEST)

        return Response(True)

class UploadProductsView(APIView):
    parser_classes = [JSONFileParser]

    def __init__(self, **kwargs):
        self._product_upload_parser = ProductUploadParser()
        self._product_business = ProductBusiness()
        super().__init__(**kwargs)

    def post(self, request):
        try:
            data = json.load(request.data['file'])
            products = self._product_upload_parser.parse(data)
            self._product_business.save_products(products)
        except InvalidDataUploadException as exception:
            return Response({ 'errors': exception.errors }, status=status.HTTP_400_BAD_REQUEST)

        return Response(True)
