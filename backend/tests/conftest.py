import pytest
from users.models import User
from recipes.models import Recipe, Ingredient, IngredientRecipe
import tempfile
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user1():
    return User.objects.create(
        username="user1",
        email='user1@gmail.com',
        password='hahahhah',
        first_name='Ivan',
        last_name='Ivanov',
    )


@pytest.fixture
def user2():
    return User.objects.create(
        username="user2",
        email='user2@gmail.com',
        password='passsss1234',
        first_name='Vanya',
        last_name='Vanov',
    )


@pytest.fixture
def ingredient1():
    return Ingredient.objects.create(
        name='Свекла',
        measurement_unit='г',
    )


@pytest.fixture
def ingredient2():
    return Ingredient.objects.create(
        name='Морковь',
        measurement_unit='г',
    )


@pytest.fixture
def ingredient3():
    return Ingredient.objects.create(
        name='Молоко',
        measurement_unit='мл',
    )


@pytest.fixture
def recipe1(user2, ingredient1, ingredient2):
    img = tempfile.NamedTemporaryFile(suffix='.jpg').name
    recipe = Recipe.objects.create(
        author=user2,
        name='Борщ',
        image=img,
        text='Вкусненько!',
        cooking_time=60,
    )
    IngredientRecipe.objects.create(
        recipe=recipe,
        ingredient=ingredient1,
        amount=10
    )
    IngredientRecipe.objects.create(
        recipe=recipe,
        ingredient=ingredient2,
        amount=20
    )

    return recipe


@pytest.fixture
def recipe2(user1, ingredient2):
    img = tempfile.NamedTemporaryFile(suffix='.jpg').name
    recipe = Recipe.objects.create(
        author=user1,
        name='Морковь по-корейски',
        image=img,
        text='Ням ням!',
        cooking_time=30,
    )
    IngredientRecipe.objects.create(
        recipe=recipe,
        ingredient=ingredient2,
        amount=10
    )

    return recipe
