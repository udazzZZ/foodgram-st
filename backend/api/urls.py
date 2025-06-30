from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, UserViewSet, IngredientViewSet
from . import reset_password_views

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += [
    path(
        "reset-password/",
        reset_password_views.reset_password_request,
        name="reset_password"
    ),
    path(
        "reset-password-confirm/<uidb64>/<token>/",
        reset_password_views.reset_password_confirm,
        name="reset_password_confirm"
    ),
]
