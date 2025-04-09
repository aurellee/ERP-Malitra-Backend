from django.urls import path
from malitra_service.views.product_views import *

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/create/", ProductCreate.as_view(), name="create-product"),
    path("products/delete/", ProductDelete.as_view(), name="delete-product"),
    path("products/update/", ProductUpdate.as_view(), name="update-product"),
    path('products/findProduct/', ProductExist.as_view(), name='product-exists'),
    path('products/withLatestPrices/', ProductListWithLatestPrices.as_view(), name='product-with-latest-prices'),
]