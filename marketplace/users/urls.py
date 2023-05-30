from django.urls import path

from .views import *

urlpatterns = [
    path("sign-out/", UserLogoutView.as_view(), name="sign-out"),
    path("sign-in", SignInView.as_view(), name="sign-in"),
    path("sign-up", RegisterView.as_view(), name="sign-up"),
    path("profile", ProfileDetailsView.as_view(), name="profile"),
    path("profile/avatar", AvatarUpdateView.as_view(), name="update avatar"),
    path("profile/password", PasswordUpdateView.as_view(), name="password"),
    path("cart", CartView.as_view(), name="cart"),
    path("basket", BasketView.as_view(), name="add_to_basket"),
]
