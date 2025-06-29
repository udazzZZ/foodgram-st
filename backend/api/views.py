from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from collections import defaultdict
from django.http import HttpResponse

from djoser.views import UserViewSet as DjoserUserViewSet
from .filters import RecipeFilter

from recipes.models import (
    Recipe, Ingredient, IngredientRecipe
)
from users.models import User, Subscription
from .serializers import (
    IngredientSerializer,
    SubscriptionSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipeShortSerializer,
    CustomUserSerializer,
)


class UserViewSet(DjoserUserViewSet):
    def get_queryset(self):
        users = User.objects.all()
        return users

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated]
            )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(subscribers__user=user)

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

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated],
    )
    def avatar(self, request):
        if request.method == 'PUT':
            if not request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if 'avatar' not in request.data:
                return Response(
                    {"error": "Поле 'avatar' обязательно"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = CustomUserSerializer(
                self.request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {"avatar": serializer.data['avatar']},
                status=status.HTTP_200_OK
            )

        if request.method == 'DELETE':
            if request.user.avatar:
                request.user.avatar.delete()
                request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        read_serializer = RecipeReadSerializer(
            recipe, context=self.get_serializer_context())
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        read_serializer = RecipeReadSerializer(
            instance, context=self.get_serializer_context()
        )
        return Response(read_serializer.data)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
    )
    def get_link(self, request, pk):
        get_object_or_404(Recipe, id=pk)
        link = request.build_absolute_uri(f'/recipes/{pk}/')
        return Response({"short-link": link}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if request.user.favorites.filter(recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            request.user.favorites.create(recipe=recipe)
            serializer = RecipeShortSerializer(
                recipe, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            in_favorite = request.user.favorites.filter(recipe=recipe).exists()

            if not in_favorite:
                return Response(
                    {"errors": "Рецепт не находится в избранном"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            request.user.favorites.filter(recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        exists = request.user.shopping_cart.filter(recipe=recipe).exists()

        if request.method == 'POST':
            if exists:
                return Response(
                    {"errors": "Рецепт уже в списке покупок"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            request.user.shopping_cart.create(recipe=recipe)
            serializer = RecipeShortSerializer(
                recipe, context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not exists:
                return Response(
                    {"errors": "Рецепт не находится в списке покупок"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            request.user.shopping_cart.filter(recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipes = user.shopping_cart.values_list('recipe', flat=True)

        ingredients = IngredientRecipe.objects.filter(
            recipe__in=recipes
        ).select_related('ingredient')

        shopping_list = defaultdict(lambda: {'unit': '', 'amount': 0})
        for item in ingredients:
            name = item.ingredient.name
            unit = item.ingredient.measurement_unit
            shopping_list[name]['unit'] = unit
            shopping_list[name]['amount'] += item.amount

        lines = ["Список покупок:\n"]
        for name, data in shopping_list.items():
            lines.append(f"{name} ({data['unit']}) — {data['amount']}")

        content = "\n".join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
