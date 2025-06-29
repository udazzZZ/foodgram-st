from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from djoser.views import UserViewSet as DjoserUserViewSet
from .filters import RecipeFilter

from recipes.models import (
    Recipe, Ingredient
)
from users.models import User, Subscription
from .serializers import (
    IngredientSerializer,
    SubscriptionSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer
)


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
