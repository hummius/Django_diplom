from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import *


class SpicificationsInline(admin.TabularInline):
    model = Specifications


class ItemImageInline(admin.TabularInline):
    model = ItemImage


class ItemInline(admin.TabularInline):
    model = Item
    readonly_fields = ["sold"]


class SubCategoryInLine(admin.TabularInline):
    model = SubCategory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ["order", "item", "count"]


@admin.action(description="Пометить как товар ограниченного тиража")
def mark_limited(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(limited=True)


@admin.action(description="Убрать метку ограниченного тиража")
def mark_unlimited(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(limited=False)


@admin.action(description="Добавить в опубликованное")
def mark_published(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(is_published=True)


@admin.action(description="Убрать из опубликованого")
def mark_unpublished(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(is_published=False)


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    inlines = [
        ItemInline,
    ]
    list_display = ["id", "title", "created_at"]
    list_display_links = ["id", "title"]
    search_fields = ["id", "title"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        SubCategoryInLine,
    ]
    list_display = ["id", "title", "sort_index"]
    list_display_links = ["id", "title"]
    ordering = ["id", "sort_index"]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "title",
                    "sort_index",
                    "image",
                ),
            },
        ),
        (
            "Тэги",
            {
                "fields": ("tags",),
            },
        ),
    ]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    actions = [
        mark_limited,
        mark_unlimited,
        mark_published,
        mark_unpublished,
    ]
    inlines = [
        ItemImageInline,
        SpicificationsInline,
    ]
    list_display = [
        "id",
        "sort_index",
        "name",
        "market",
        "quantity",
        "description_short",
        "category",
        "is_published",
        "limited",
    ]
    list_display_links = ["id", "name"]
    ordering = ["id", "sort_index", "-name", "market"]
    search_fields = ["name", "description", "market"]
    readonly_fields = ["sold"]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "market",
                    "name",
                    "description",
                    "quantity",
                    "category",
                    "subcategory",
                ),
            },
        ),
        (
            "Ценновые опции",
            {
                "fields": ("price", "discount"),
            },
        ),
        (
            "Индекс сортировки",
            {
                "fields": ("sort_index",),
            },
        ),
        (
            "Изображения",
            {
                "fields": ("preview",),
            },
        ),
        (
            "Публикация",
            {
                "fields": ("is_published",),
            },
        ),
        (
            "Доп. опции",
            {
                "fields": ("limited",),
                "classes": ("collapse",),
                "description": 'Дополнительные опции. Поле "limited" для пометки товара ограниченного тиража.',
            },
        ),
    ]

    def description_short(self, obj: Item) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "item", "rate", "created_at", "author", "text_short"]
    list_display_links = ["id", "item"]
    search_fields = ["id", "item", "author"]

    def text_short(self, obj: Review) -> str:
        if len(obj.text) < 48:
            return obj.text
        return obj.text[:48] + "..."


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline,
    ]
    list_display = ["id", "user", "created_at", "city", "address", "totalCost"]
    list_display_links = ["id", "user"]
    search_fields = ["id", "user"]
    fieldsets = [
        (
            None,
            {
                "fields": ("user", "city", "address", "totalCost"),
            },
        ),
        (
            "Иформация",
            {
                "fields": (
                    "fullName",
                    "email",
                    "phone",
                    "paymentType",
                    "status",
                    "deliveryType",
                ),
            },
        ),
    ]


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ["id", "item", "salePrice", "dateFrom", "dateTo"]
    list_display_links = ["id", "item"]
    search_fields = ["id", "item"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "order", "number", "name", "payment", "created_at"]
    list_display_links = ["id", "user", "order"]
    search_fields = ["id", "user", "order", "payment"]
    readonly_fields = ["id", "user", "order", "number", "name", "payment", "created_at"]
