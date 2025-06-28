from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import (
    Recipe, Ingredient, IngredientRecipe,
    Favorite, ShoppingCart
)
from users.models import User, Subscription
from .serializers import (
    RecipeSerializer, RecipeCreateSerializer, IngredientSerializer,
    SubscriptionSerializer
)


def add_obj(request, pk, model_class):
    recipe = get_object_or_404(Recipe, pk=pk)
    if model_class.objects.filter(user=request.user, recipe=recipe).exists():
        return {'errors': 'Объект уже существует'}, status.HTTP_400_BAD_REQUEST
    model_class.objects.create(user=request.user, recipe=recipe)
    serializer = RecipeSerializer(recipe, context={'request': request})
    return serializer.data, status.HTTP_201_CREATED


def del_obj(request, pk, model_class):
    """Удаляет объект из модели связи."""
    recipe = get_object_or_404(Recipe, pk=pk)
    obj = model_class.objects.filter(user=request.user, recipe=recipe)
    if not obj.exists():
        return {'errors': 'Объект не существует'}, status.HTTP_400_BAD_REQUEST
    obj.delete()
    return {}, status.HTTP_204_NO_CONTENT


def create_shopping_list(ingredients):
    shopping_list = "Список покупок:\n\n"
    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['amount']
        shopping_list += f"{name} ({unit}) — {amount}\n"
    return shopping_list


class UserViewSet(DjoserUserViewSet):
    def get_queryset(self):
        users = User.objects.all()
        return users

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated]
            )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(subscriptions__user=user)

        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(
            subscriptions, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        author = self.get_object()
        user = request.user

        if request.method == 'POST':
            if author == user:
                return Response(
                    {"errors": "Нельзя подписаться на самого себя"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {"errors": "Вы уже подписаны на этого пользователя"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user, author=author).first()
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Вы не подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST
            )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        if request.method == "POST":
            data, status_code = add_obj(request, pk, Favorite)
            return Response(data, status=status_code)
        data, status_code = del_obj(request, pk, Favorite)
        return Response(data, status=status_code)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            data, status_code = add_obj(request, pk, ShoppingCart)
            return Response(data, status=status_code)
        data, status_code = del_obj(request, pk, ShoppingCart)
        return Response(data, status=status_code)

    @action(methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user).values(
                'ingredient__name',
                'ingredient__measurement_unit').annotate(
                    amount=Sum('amount')).order_by('ingredient__name')

        shopping_list = create_shopping_list(ingredients)
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format('shopping_list.txt')
        )
        return response
