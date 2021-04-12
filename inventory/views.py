import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import status

from .models import Product
from .business_logic import ArticleUploadParser, InvalidDataUploadException, save_article_uploads

class ProductSerializer(ModelSerializer):
  class Meta:
    model: Product
    fields: ['name']

class ProductListView(APIView):
  def get(self, request):
    data = { 'a': 1 }
    return Response(data)

class JSONFileParser(FileUploadParser):
  media_type = 'application/json'

class UploadArticlesView(APIView):
  parser_classes = [JSONFileParser]

  def post(self, request):
    file_dict = json.load(request.data['file'])
    try:
      articles = ArticleUploadParser().parse(file_dict)
      save_article_uploads(articles)
    except InvalidDataUploadException as exception:
      return Response({ 'errors': exception.errors }, status=status.HTTP_400_BAD_REQUEST)

    return Response(True)

