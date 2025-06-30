from django.contrib import admin
from .models import User, Subscription


class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username')
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar',
        'is_subscribed',
    )
    list_display_links = ('email',)
    list_editable = (
        'username',
        'first_name',
        'last_name',
        'avatar',
        'is_subscribed',
    )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    list_display_links = ('user',)
    list_editable = ('author',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
