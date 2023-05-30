from rest_framework import serializers

from market.models import *
from users.models import *
from taggit.models import Tag


class BasketSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
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
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        ]

    def get_price(self, obj):
        cart = Cart(self.context)
        return cart.cart[str(obj.id)]["price"]

    def get_count(self, obj):
        cart = Cart(self.context)
        count = cart.cart[str(obj.id)]["count"]
        return count

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
        return obj.count_reviews()

    def get_rating(self, obj):
        return obj.get_rating()
