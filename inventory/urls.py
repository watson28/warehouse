from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('articles/upload', views.UploadArticlesView.as_view(), name='upload-articles'),
]
