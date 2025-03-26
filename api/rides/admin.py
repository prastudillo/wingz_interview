from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Ride, RideEvent, User


class UserAdmin(BaseUserAdmin):
    # Include 'role'
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "role", "phone_number")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "role",
                    "phone_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")


admin.site.register(User, UserAdmin)
admin.site.register(Ride)
admin.site.register(RideEvent)
