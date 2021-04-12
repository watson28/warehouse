from .models import Article

class InvalidDataUploadException(Exception):
  def __init__(self, *errors):
    self.errors = errors


class ArticleUploadParser:
  def parse(self, upload_articles_content):
    articles = self._parse_list_field(upload_articles_content, 'inventory', 'root')
    return self._parse_article_list(articles)

  def _parse_article_list(self, articles):
    article_models = []
    format_errors = []
    for index, article in enumerate(articles):
      try:
        article_model = self._parse_article(article, index)
        article_models.append(article_model)
      except InvalidDataUploadException as exception:
        format_errors.append(str(exception))

    if len(format_errors) > 0:
      raise InvalidDataUploadException(*format_errors)

    return article_models

  def _parse_article(self, article, index):
    obj_context = f'inventory[{index}]'
    id = self._parse_numeric_field(article, 'art_id', obj_context)
    name = self._parse_field(article, 'name', obj_context)
    stock = self._parse_numeric_field(article, 'stock', obj_context)

    return Article(id=id, name=name, stock=stock)
  
  def _parse_field(self, obj, field_name, obj_context):
    if field_name not in obj:
      raise InvalidDataUploadException(f'attribute {obj_context}.{field_name}: not found')
    
    return obj[field_name]

  def _parse_numeric_field(self, obj, field_name, obj_context):
    value = self._parse_field(obj, field_name, obj_context)
    try:
      return int(value)
    except ValueError:
      raise InvalidDataUploadException(f'attribute {obj_context}.{field_name}: expected number')

  def _parse_list_field(self, obj, field_name, obj_context):
    value = self._parse_field(obj, field_name, obj_context)
    if type(value) is not list:
      raise InvalidDataUploadException(f'attribute {obj_context}.{field_name}: expected list')
    
    return value

def save_article_uploads(articles):
  upload_ids = map(lambda article: article.id, articles)
  queryset_existing_ids = Article.objects.filter(id__in=upload_ids).values('id')
  existing_ids = list(map(lambda qs: qs['id'], queryset_existing_ids))
  existing_articles = filter(lambda article: article.id in existing_ids, articles)
  not_existing_articles = filter(lambda article: article.id not in existing_ids, articles)

  Article.objects.bulk_update(existing_articles, fields=['name', 'stock'], batch_size=50)
  Article.objects.bulk_create(not_existing_articles, batch_size=50)


