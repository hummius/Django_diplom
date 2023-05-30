from django.urls import path
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="categories"),
    path("tags/", TagListView.as_view(), name="tags"),
    path("product/<int:id>/", ItemDetailsView.as_view(), name="product"),
    path(
        "product/<int:id>/reviews/",
        ItemReviewCreateView.as_view(),
        name="product_review",
    ),
    path("products/popular/", ProductsPopularView.as_view(), name="products_popular"),
    path("products/limited/", ProductsLimitedView.as_view(), name="products_limited"),
    path("banners", BannerView.as_view(), name="banners"),
    path("catalog/", CatalogView.as_view(), name="catalog"),
    path("orders", OrdersListView.as_view(), name="orders"),
    path("order/<int:id>", MakeOrderView.as_view(), name="make_order"),
    path("payment/<int:id>", PaymentView.as_view(), name="payment"),
    path("sales", SalesView.as_view(), name="sales"),
]
