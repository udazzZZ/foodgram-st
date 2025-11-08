from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, UserViewSet, IngredientViewSet, run_bible_verse_task, run_book_task, get_task_status

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
    path('book/', run_book_task, name='book'),
    path('bible_verse/', run_bible_verse_task, name='bible_verse'),
    path('task_status/<str:task_id>/', get_task_status)
]
