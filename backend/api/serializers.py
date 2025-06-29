from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import base64

from recipes.models import Recipe, Ingredient, IngredientRecipe
from users.models import Subscription

User = get_user_model()
MIN_INGREDIENT_AMOUNT = 1
MAX_INGREDIENT_AMOUNT = 1000


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar"
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriptions.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password"
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        max_value=MAX_INGREDIENT_AMOUNT,
    )


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        ]

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return request.user.is_authenticated and obj.favorited_by.filter(
            user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return request.user.is_authenticated and obj.in_carts_of.filter(
            user=request.user
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        write_only=True
    )
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        ]
        read_only_fields = ("author",)

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Это поле обязательно для заполнения."}
            )

        ids = [item["id"] for item in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться."})
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredients_data:
            instance.recipe_ingredients.all().delete()
            self._save_ingredients(instance, ingredients_data)
        return instance

    def _save_ingredients(self, recipe, ingredients_data):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                ingredient=ing["id"],
                amount=ing["amount"]
            ) for ing in ingredients_data
        ])


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
