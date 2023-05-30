import datetime
from _decimal import Decimal

from django.db import models
from django.contrib.auth.models import User

from market.models import Item, Sales
from marketplace import settings


def profiles_avatars_directory_path(instance: "Profile", filename: str) -> str:
    return "profile/profile_{pk}/avatar/{filename}".format(
        pk=instance.pk, filename=filename
    )


class Profile(models.Model):
    class Meta:
        verbose_name = "профиль пользователя"
        verbose_name_plural = "профили пользователей"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(
        max_length=100, blank=True, null=True, default="", verbose_name="полное имя"
    )
    phone = models.CharField(
        null=True, blank=True, default="", max_length=16, verbose_name="телефон"
    )
    avatar = models.ImageField(
        verbose_name="аватар",
        upload_to=profiles_avatars_directory_path,
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=40, null=True, blank=True, default="", verbose_name="город"
    )
    address = models.CharField(
        max_length=80, null=True, blank=True, default="", verbose_name="адрес"
    )

    def __str__(self):
        return f"{self.user.username}"

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, item, quantity):
        sale = Sales.objects.filter(item_id=item.id)
        item_id = str(item.id)

        if item_id not in self.cart:
            if sale and sale[0].dateFrom <= datetime.date.today() <= sale[0].dateTo:
                self.cart[item_id] = {
                    "id": item_id,
                    "count": quantity,
                    "price": str(sale[0].salePrice),
                }
            else:
                self.cart[item_id] = {
                    "id": item_id,
                    "count": quantity,
                    "price": str(item.price),
                }
        else:
            self.cart[item_id]["count"] += quantity

        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, item, count):
        item_id = str(item.id)
        if item_id in self.cart:
            if self.cart[item_id]["count"] <= count:
                del self.cart[item_id]
                self.save()
            else:
                self.cart[item_id]["count"] -= count
                self.save()

    def __iter__(self):
        full_price = [0]
        item_ids = self.cart.keys()
        items = Item.objects.filter(id__in=item_ids)
        for item in items:
            self.cart[str(item.id)]["item"] = item

        for value in self.cart.values():
            value["price"] = Decimal(value["price"])
            value["total_price"] = value["price"] * int(value["count"])
            full_price[0] += value["total_price"]
            yield value

    def __len__(self):
        full_price = [0]
        for value in self.cart.values():
            value["total_price"] = float(value["price"]) * int(value["count"])
            full_price[0] += int(value["total_price"])

        return full_price[0]

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
