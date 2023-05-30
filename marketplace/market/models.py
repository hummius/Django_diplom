from django.contrib.auth.models import User
from django.db import models
from taggit.managers import TaggableManager


class Market(models.Model):
    class Meta:
        verbose_name = "магазин"
        verbose_name_plural = "магазины"

    title = models.CharField(max_length=100, unique=True, verbose_name="название")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создан")

    def __str__(self):
        return f'Market(pk="{self.pk}", title="{self.title}")'


def category_icons_directory_path(instance: "Category", filename: str) -> str:
    return "categories/category_{pk}/icon/{filename}".format(
        pk=instance.pk, filename=filename
    )


class Category(models.Model):
    class Meta:
        ordering = ["sort_index"]
        verbose_name = "категория товара"
        verbose_name_plural = "категории товара"

    title = models.CharField(max_length=100, unique=True, verbose_name="название")
    image = models.ImageField(
        null=True, upload_to=category_icons_directory_path, verbose_name="иконка"
    )
    sort_index = models.PositiveIntegerField(
        default=0, verbose_name="индекс сортировки"
    )
    active = models.BooleanField(default=False, verbose_name="статус активности")
    tags = TaggableManager()

    def __str__(self):
        return f'Category(pk="{self.pk}", title="{self.title}")'

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url

    def change_status(self):
        item = Item.objects.filter(category_id=self.pk, is_published=True)
        if item:
            self.active = True
            self.save()
        else:
            self.active = False
            self.save()


def subcategory_icons_directory_path(instance: "SubCategory", filename: str) -> str:
    return "subcategories/category_{pk}/icon/{filename}".format(
        pk=instance.pk, filename=filename
    )


class SubCategory(models.Model):
    class Meta:
        ordering = ["sort_index"]
        verbose_name = "подкатегория товара"
        verbose_name_plural = "подкатегории товара"

    title = models.CharField(max_length=100, unique=True, verbose_name="название")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="категория"
    )
    image = models.ImageField(
        null=True, upload_to=subcategory_icons_directory_path, verbose_name="иконка"
    )
    sort_index = models.PositiveIntegerField(
        default=0, verbose_name="индекс сортировки"
    )
    active = models.BooleanField(default=False, verbose_name="статус активности")

    def __str__(self):
        return (
            f'Category(="{self.category.title}", pk="{self.pk}, "title="{self.title}")'
        )

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url

    def change_status(self):
        item = Item.objects.filter(category_id=self.pk)
        if item:
            self.active = True
            self.save()
        else:
            self.active = False
            self.save()


def item_preview_directory_path(instance: "Item", filename: str) -> str:
    return "items/item_{pk}/preview/{filename}".format(
        pk=instance.pk, filename=filename
    )


class Item(models.Model):
    class Meta:
        ordering = ["name", "price"]
        verbose_name = "товар"
        verbose_name_plural = "товар"

    name = models.CharField(max_length=200, unique=True, verbose_name="наименование")
    sort_index = models.IntegerField(default=0, verbose_name="индекс сортировки")
    preview = models.ImageField(
        null=True,
        blank=True,
        upload_to=item_preview_directory_path,
        verbose_name="превью",
    )
    description = models.TextField(
        null=False, blank=True, default="", verbose_name="краткое описание"
    )
    price = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, verbose_name="цена"
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="кол-во")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создано")
    is_published = models.BooleanField(default=False, verbose_name="публикация")
    sold = models.PositiveIntegerField(default=0, verbose_name="продано")
    market = models.ForeignKey(
        Market, null=False, on_delete=models.CASCADE, verbose_name="магазин"
    )
    category = models.ForeignKey(
        Category, null=False, on_delete=models.CASCADE, verbose_name="категория товара"
    )
    subcategory = models.ForeignKey(
        SubCategory,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="подкатегория товара",
    )
    free_delivery = models.BooleanField(
        default=False, verbose_name="бесплатная доставка"
    )
    reviews = models.PositiveIntegerField(default=0, verbose_name="отзывов")
    discount = models.PositiveIntegerField(default=0, null=False, verbose_name="скидка")
    limited = models.BooleanField(default=False, verbose_name="ограниченный тираж")

    def __str__(self):
        return f'Item(pk="{self.pk}", name="{self.name}")'

    def final_price(self):
        return round(self.price * (100 - self.discount) / 100, 2)

    def count_reviews(self):
        reviews = [review for review in Review.objects.filter(item_id=self.pk)]
        return len(reviews)

    def get_rating(self):
        ratings = [review.rate for review in Review.objects.filter(item_id=self.pk)]
        if sum(ratings) != 0:
            result = sum(ratings) / len(ratings)
            return result
        return 0


class Sales(models.Model):
    class Meta:
        verbose_name = "скидка"
        verbose_name_plural = "скидки"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="товар")
    salePrice = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="скидочная цена"
    )
    dateFrom = models.DateField(verbose_name="дата старта")
    dateTo = models.DateField(verbose_name="дата окончания")


def item_image_directory_path(instance: "ItemImage", filename: str) -> str:
    return "items/itemimage_{pk}/images/{filename}".format(
        pk=instance.pk, filename=filename
    )


class ItemImage(models.Model):
    class Meta:
        verbose_name = "изображение товара"
        verbose_name_plural = "изображения товара"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=item_image_directory_path)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url


class Review(models.Model):
    RATE_CHOICES = (
        (1, "Ужасно"),
        (2, "Плохо"),
        (3, "Средне"),
        (4, "Хорошо"),
        (5, "Отлично"),
    )

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"

    author = models.CharField(max_length=100, verbose_name="автор отзыва")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="товар")
    email = models.EmailField(verbose_name="email автора")
    text = models.TextField(verbose_name="текст отзыва")
    rate = models.PositiveIntegerField(choices=RATE_CHOICES, verbose_name="оценка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создано")


class Specifications(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="товар")
    name = models.CharField(max_length=100, verbose_name="тип спецификации")
    value = models.CharField(max_length=100, verbose_name="значение")


class Order(models.Model):
    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создано")
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name="пользователь"
    )
    fullName = models.CharField(null=True, max_length=100, verbose_name="полное имя")
    email = models.EmailField(null=True, verbose_name="e-mail")
    phone = models.CharField(null=True, max_length=20, verbose_name="телефон")
    city = models.CharField(null=True, max_length=100, verbose_name="город")
    address = models.CharField(null=True, max_length=200, verbose_name="адрес")
    paymentType = models.CharField(max_length=50, null=True, verbose_name="тип оплаты")
    totalCost = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="полная стоимость"
    )
    status = models.CharField(
        default="not_accepted", max_length=50, verbose_name="статус заказа"
    )
    deliveryType = models.CharField(
        default="ordinary", max_length=20, verbose_name="тип доставки"
    )


class OrderItem(models.Model):
    class Meta:
        verbose_name = "позиция в заказе"
        verbose_name_plural = "позиции в заказе"

    item = models.ForeignKey(
        Item, on_delete=models.PROTECT, verbose_name="позиция заказа"
    )
    price = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="стоимость"
    )
    count = models.PositiveIntegerField(verbose_name="кол-во")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="заказ")


class Payment(models.Model):
    class Meta:
        verbose_name = "платеж"
        verbose_name_plural = "платежи"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="пользователь"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="заказ")
    number = models.CharField(max_length=100, verbose_name="номер карты")
    name = models.CharField(max_length=100, verbose_name="имя владельца карты")
    payment = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="сумма платежа"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создано")
