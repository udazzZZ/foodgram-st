from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from recipes.models import (
    Recipe, Ingredient, IngredientRecipe,
    Favorite, ShoppingCart
)
from users.models import User
from .serializers import (
    RecipeSerializer, RecipeCreateSerializer,
    UserSerializer, IngredientSerializer
)
from .permissions import ReadOnlyOrAuthenticated


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


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (ReadOnlyOrAuthenticated,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (ReadOnlyOrAuthenticated,)
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
