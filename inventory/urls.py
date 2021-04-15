from django.urls import path

from . import views

urlpatterns = [
    path('products/availability', views.ProductsAvailabilityView.as_view(), name='products-availability'),
    path('products/<int:product_id>/sell', views.SellProductView.as_view(), name='products-availability'),
    path('products/upload', views.UploadProductsView.as_view(), name='upload-products'),
    path('articles/upload', views.UploadArticlesView.as_view(), name='upload-articles'),
]
