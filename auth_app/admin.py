from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import ActivationToken


class ActivationTokenInline(admin.TabularInline):
    model = ActivationToken
    readonly_fields = ["token", "created_at", "is_expired_display"]
    extra = 0

    def is_expired_display(self, obj):
        return obj.is_expired()

    is_expired_display.short_description = "Abgelaufen?"
    is_expired_display.boolean = True


class CustomUserAdmin(UserAdmin):
    inlines = [ActivationTokenInline]
    list_display = [
        "username",
        "email",
        "is_active",
        "is_staff",
        "date_joined",
    ]
    list_filter = ["is_active", "is_staff"]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(ActivationToken)
class ActivationTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "is_expired_display"]
    readonly_fields = ["token", "created_at"]

    def is_expired_display(self, obj):
        return obj.is_expired()

    is_expired_display.short_description = "Abgelaufen?"
    is_expired_display.boolean = True
