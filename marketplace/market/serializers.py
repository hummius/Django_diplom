from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination

from .models import *
from taggit.models import Tag


class CatalogSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    freeDelivery = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            "id",
            "category",
            "price",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        ]

    def get_date(self, obj):
        return obj.created_at.strftime(
            "%a %b %d %Y %X %Z%z (Coordinated Universal Time)"
        )

    def get_title(self, obj):
        return obj.name

    def get_freeDelivery(self, obj):
        return obj.free_delivery

    def get_images(self, obj):
        result = [
            {"src": image.image_url, "alt": "Image alt string"}
            for image in ItemImage.objects.filter(item_id=obj.id)
        ]
        if result:
            return result
        return [{"src": "", "alt": "Image alt string"}]

    def get_tags(self, obj):
        return [
            {"id": tag.id, "name": tag.name}
            for tag in Tag.objects.filter(category=obj.category_id)
        ]

    def get_reviews(self, obj):
        return obj.count_reviews()

    def get_rating(self, obj):
        return obj.get_rating()


class ItemDetailsSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    freeDelivery = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            "id",
            "category",
            "price",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        ]

    def get_date(self, obj):
        return obj.created_at.strftime(
            "%a %b %d %Y %X %Z%z (Coordinated Universal Time)"
        )

    def get_title(self, obj):
        return obj.name

    def get_freeDelivery(self, obj):
        return obj.free_delivery

    def get_images(self, obj):
        result = [
            {"src": image.image.url, "alt": "Image alt string"}
            for image in ItemImage.objects.filter(item_id=obj.id)
        ]
        if result:
            return result
        return [{"src": "", "alt": "Image alt string"}]

    def get_tags(self, obj):
        return [
            {"id": tag.id, "name": tag.name}
            for tag in Tag.objects.filter(category=obj.category_id)
        ]

    def get_reviews(self, obj):
        result = [
            {
                "author": rev.author,
                "email": rev.email,
                "text": rev.text,
                "rate": rev.rate,
                "date": rev.created_at,
            }
            for rev in Review.objects.filter(item_id=obj.id)
        ]
        if result:
            return result
        return None

    def get_specifications(self, obj):
        return [
            {
                "name": spec.name,
                "value": spec.value,
            }
            for spec in Specifications.objects.filter(item_id=obj.id)
        ]

    def get_rating(self, obj):
        return obj.get_rating()


class OrderItemDetailsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    freeDelivery = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "category",
            "price",
            "date",
            "count",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        ]

    def get_id(self, obj):
        return obj.item.id

    def get_category(self, obj):
        return obj.item.category_id

    def get_price(self, obj):
        return obj.price * obj.count

    def get_date(self, obj):
        return obj.item.created_at.strftime(
            "%a %b %d %Y %X %Z%z (Coordinated Universal Time)"
        )

    def get_title(self, obj):
        return obj.item.name

    def get_description(self, obj):
        return obj.item.description

    def get_freeDelivery(self, obj):
        return obj.item.free_delivery

    def get_images(self, obj):
        result = [
            {"src": image.image_url, "alt": "Image alt string"}
            for image in ItemImage.objects.filter(item_id=obj.item_id)
        ]
        if result:
            return result
        return [{"src": "", "alt": "Image alt string"}]

    def get_tags(self, obj):
        return [
            {"id": tag.id, "name": tag.name}
            for tag in Tag.objects.filter(category=obj.item.category_id)
        ]

    def get_reviews(self, obj):
        return obj.item.count_reviews()

    def get_rating(self, obj):
        return obj.item.get_rating()


class OrderSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        ]

    def get_fullName(self, obj):
        return obj.user.profile.fullName

    def get_createdAt(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")

    def get_email(self, obj):
        return obj.user.email

    def get_phone(self, obj):
        return obj.user.profile.phone

    def get_products(self, obj):
        order_items = OrderItem.objects.select_related("item").filter(order_id=obj.id)
        serializer = OrderItemDetailsSerializer(order_items, many=True)
        return serializer.data


class SalesSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Sales
        fields = [
            "id",
            "price",
            "salePrice",
            "dateFrom",
            "dateTo",
            "title",
            "images",
            "tags",
        ]

    def get_id(self, obj):
        return obj.item_id

    def get_price(self, obj):
        return obj.item.price

    def get_title(self, obj):
        return obj.item.name

    def get_images(self, obj):
        result = [
            {"src": image.image_url, "alt": "Image alt string"}
            for image in ItemImage.objects.filter(item_id=obj.item.id)
        ]
        if result:
            return result
        return [{"src": "", "alt": "Image alt string"}]

    def get_tags(self, obj):
        return [
            {"id": tag.id, "name": tag.name}
            for tag in Tag.objects.filter(category=obj.item.category_id)
        ]
