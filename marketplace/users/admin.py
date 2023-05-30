from django.contrib import admin
from django.contrib.auth.models import User

from .models import Profile


class UserProfileInLine(admin.StackedInline):
    model = Profile
    verbose_name_plural = "Профиль пользователя"


class UserAdmin(admin.ModelAdmin):
    inlines = [
        UserProfileInLine,
    ]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
