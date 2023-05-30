from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Cart
from .models import (
    Category,
    SubCategory,
    Item,
    Review,
    Order,
    OrderItem,
    Sales,
    Payment,
)
from .serializers import (
    CatalogSerializer,
    ItemDetailsSerializer,
    OrderSerializer,
    OrderItemDetailsSerializer,
    SalesSerializer,
)
from taggit.models import Tag


class CategoryListView(APIView):
    """Представление категорий товара"""

    name = "get_categories"
    description = "get catalog menu"

    def get(self, request: Request) -> Response:
        for category in Category.objects.all():
            category.change_status()

        for subcategory in SubCategory.objects.all():
            subcategory.change_status()

        categories = [
            {
                "id": categories.id,
                "title": categories.title,
                "image": {"src": categories.image_url, "alt": "Image alt string"},
                "subcategories": [
                    {
                        "id": subcategories.id,
                        "title": subcategories.title,
                        "image": {
                            "src": subcategories.image_url,
                            "alt": "Image alt string",
                        },
                    }
                    for subcategories in SubCategory.objects.filter(
                        category_id=categories.id, active=True
                    )
                ],
            }
            for categories in Category.objects.filter(active=True)
        ]

        return Response(categories)


class TagListView(APIView):
    """Представление тэгов"""

    name = "get_tags"
    description = "Get tags"

    def get(self, request: Request) -> Response:
        if request.data:
            tags = [
                {"id": tag.id, "name": tag.name}
                for tag in Tag.objects.filter(object_id=request.data["category"])
            ]
            return Response(tags)
        tags = [{"id": tag.id, "name": tag.name} for tag in Tag.objects.all()]
        return Response(tags)


class CatalogView(generics.ListAPIView):
    """Представление каталога"""

    serializer_class = CatalogSerializer

    def get_queryset(self) -> QuerySet:
        data = self.request.query_params
        name = data.get("filter[name]")
        min_price = int(data.get("filter[minPrice]"))
        max_price = int(data.get("filter[maxPrice]"))
        free_delivery = data.get("filter[freeDelivery]")
        available = data.get("filter[available]")
        sort = data.get("sort")
        sort_type = data.get("sortType")
        limit = int(data.get("limit"))

        if name:
            items = Item.objects.filter(
                is_published=True, name__contains=name, price__gt=min_price, price__lt=max_price
            )
        else:
            items = Item.objects.filter(
                is_published=True, price__gt=min_price, price__lt=max_price
            )
        if free_delivery == "true":
            items = items.filter(free_delivery=True)

        if available == "true":
            items = items.exclude(quantity=0)

        if sort == "price":
            if sort_type == "dec":
                items = items.order_by("-price")
            if sort_type == "inc":
                items = items.order_by("price")

        if sort == "reviews":
            if sort_type == "dec":
                items = sorted(
                    items,
                    key=lambda x: len(Review.objects.filter(item_id=x.id)),
                    reverse=True,
                )
            if sort_type == "inc":
                items = sorted(
                    items, key=lambda x: len(Review.objects.filter(item_id=x.id))
                )

        if sort == "date":
            if sort_type == "dec":
                items = items.order_by("-created_at")
            if sort_type == "inc":
                items = items.order_by("created_at")

        if sort == "rating":
            if sort_type == "dec":
                items = sorted(items, key=lambda x: x.get_rating(), reverse=True)
            if sort_type == "inc":
                items = sorted(items, key=lambda x: x.get_rating())

        queryset = items[:limit]
        return queryset

    def get(self, request: Request, *args, **kwargs) -> Response:
        items = self.get_queryset()
        paginator = Paginator(items, 6)
        last_page = paginator.num_pages
        serializer = CatalogSerializer(
            paginator.get_page(int(self.request.query_params["currentPage"])), many=True
        )

        response = {
            "items": serializer.data,
            "currentPage": int(self.request.query_params["currentPage"]),
            "lastPage": last_page,
        }

        return Response(response)


class ItemDetailsView(APIView):
    """Представление деталей товара"""

    serializer_class = ItemDetailsSerializer

    def get_queryset(self, request: Request, id: int) -> QuerySet:
        queryset = Item.objects.get(id=id)
        return queryset

    def get(self, request: Request, id: int) -> Response:
        item = self.get_queryset(request, id)
        serializer = ItemDetailsSerializer(item)
        return Response(serializer.data)


class ItemReviewCreateView(LoginRequiredMixin, APIView):
    """Представлние отзывов на товар"""

    serializer_class = ItemDetailsSerializer
    permission_denied_message = "Вы не авторизованы"

    def get_queryset(self, request: Request, id: int) -> QuerySet:
        queryset = Item.objects.get(id=id)
        return queryset

    def get(self, request: Request, id: int) -> Response:
        item = self.get_queryset(request, id)
        serializer = ItemDetailsSerializer(item)
        return Response(serializer.data)

    def post(self, request: Request, id: int) -> Response:
        print(request.data)
        data = request.data
        Review.objects.create(
            author=data["author"],
            email=data["email"],
            text=data["text"],
            rate=int(data["rate"]),
            item=Item.objects.get(id=id),
        )
        item = self.get_queryset(request, id)
        serializer = ItemDetailsSerializer(item)
        return Response(serializer.get_reviews(item))


class ProductsPopularView(APIView):
    """Представление популярных товаров"""

    serializer_class = CatalogSerializer

    def get(self, request: Request) -> Response:
        items = (
            Item.objects.filter(is_published=True)
            .order_by("sort_index", "-sales")
            .exclude(sort_index=0)[:8]
        )
        serializer = CatalogSerializer(items, many=True)

        return Response(serializer.data)


class ProductsLimitedView(APIView):
    """Представление лимитированных товаров"""

    serializer_class = CatalogSerializer

    def get(self, request: Request) -> Response:
        items = Item.objects.filter(is_published=True, limited=True)[:16]
        serializer = CatalogSerializer(items, many=True)

        return Response(serializer.data)


class BannerView(APIView):
    """Представление баннеров"""

    serializer_class = CatalogSerializer

    def get(self, request: Request) -> Response:
        items = Item.objects.filter(is_published=True)
        Paginator(items, 4)
        serializer = CatalogSerializer(items, many=True)

        return Response(serializer.data)


class SalesView(APIView):
    """Представление скидок"""

    serializer_class = SalesSerializer

    def get(self, request: Request) -> Response:
        sales = Sales.objects.select_related("item").all()
        paginator = Paginator(sales, 4)
        last_page = paginator.num_pages
        serializer = SalesSerializer(sales, many=True)

        response = {
            "items": serializer.data,
            "currentPage": int(self.request.query_params["currentPage"]),
            "lastPage": last_page,
        }
        return Response(response)


class OrdersListView(LoginRequiredMixin, APIView):
    """Представление заказов"""

    serializer_classes = OrderSerializer, OrderItemDetailsSerializer
    serializer_class = ItemDetailsSerializer

    def get(self, request: Request) -> Response:
        Order.objects.filter(status="not_accepted").delete()
        orders = Order.objects.order_by("-created_at").filter(user_id=request.user.id)
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        Order.objects.filter(status="not_accepted").delete()
        order = request.data
        items_list = []
        total_cost = 0

        for item in order:
            total_cost += float(item["price"]) * float(item["count"])

        order_obj = Order.objects.create(
            user=request.user,
            totalCost=total_cost,
            fullName=request.user.profile.fullName,
            email=request.user.email,
            phone=request.user.profile.phone,
            city=request.user.profile.city,
            address=request.user.profile.address,
            deliveryType="free",
            paymentType="online",
        )

        for item in order:
            item_obj = Item.objects.get(id=item["id"])
            items_list.append(item_obj)
            OrderItem.objects.create(
                item=item_obj, price=item["price"], count=item["count"], order=order_obj
            )

        return Response({"orderId": order_obj.id})


class MakeOrderView(LoginRequiredMixin, APIView):
    """Представление создания заказа"""

    serializer_classes = OrderSerializer, OrderItemDetailsSerializer

    def get(self, request, id):
        order = Order.objects.get(id=id)

        if request.user.id == order.user_id:
            serializer = OrderSerializer(order)

            return Response(serializer.data)

        return Response(status=404)

    def post(self, request, id):
        data = request.data
        order = Order.objects.get(id=id)
        order.fullName = data["fullName"]
        order.email = data["email"]
        order.deliveryType = data["deliveryType"]
        order.city = data["city"]
        order.address = data["address"]
        order.paymentType = data["paymentType"]
        order.status = "payment"

        order.save()
        Cart(request).clear()

        return Response({"orderId": id})


class PaymentView(APIView, LoginRequiredMixin):
    """Представление оплаты заказа"""

    def post(self, request, id):
        name = request.data["name"]
        number = request.data["number"]
        month = request.data["month"]
        year = request.data["year"]
        code = request.data["code"]

        order = Order.objects.get(id=id)
        Payment.objects.create(
            user=request.user,
            order=order,
            number=number,
            name=name,
            payment=order.totalCost,
        )
        order.status = "accepted"
        order.save()
        return Response()
