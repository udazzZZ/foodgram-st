from django.contrib import admin
from .models import (
    Ingredient,
    Recipe,
    IngredientRecipe,
    ShoppingCart,
    Favorite,
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_display_links = ('name',)
    list_editable = ('measurement_unit',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    list_display_links = ('name',)
    list_editable = ('author',)
    search_fields = (
        'name',
        'author__email',
    )
    readonly_fields = ('get_favorite_count',)

    def get_favorite_count(self, obj):
        return obj.favorited_by.count()

    get_favorite_count.short_description = 'Добавлений в избранное'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_display_links = ('user',)
    list_editable = ('recipe',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_display_links = ('user',)
    list_editable = ('recipe',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
