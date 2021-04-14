from django.urls import path

from . import views

urlpatterns = [
    path('products/upload', views.UploadProductsView.as_view(), name='upload-products'),
    path('articles/upload', views.UploadArticlesView.as_view(), name='upload-articles'),
]
