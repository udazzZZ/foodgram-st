from http import HTTPStatus
from django.urls import reverse
import pytest
from rest_framework.authtoken.models import Token


@pytest.mark.parametrize(
    'name',
    ('api:recipes-list', 'api:users-list')
)
@pytest.mark.django_db
def test_pages_available_for_anonymous(client, name):
    url = reverse(name)
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_users_pk_available_for_anonymous(client, user1):
    url = reverse('api:users-detail', kwargs={'id': user1.id})
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_recipes_pk_available_for_anonymous(client, recipe1):
    url = reverse('api:recipes-detail', kwargs={'pk': recipe1.pk})
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_download_cart_for_anonymous(client):
    url = reverse('api:recipes-download-shopping-cart')
    response = client.get(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_add_to_cart_for_anonymous(client, recipe1):
    url = reverse('api:recipes-shopping-cart', kwargs={'pk': recipe1.pk})
    response = client.post(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    'name',
    ('api:recipes-shopping-cart', 'api:recipes-favorite')
)
@pytest.mark.django_db
def test_add_recipe_for_auth(api_client, recipe1, user1, name):
    token = Token.objects.create(user=user1)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse(name, kwargs={'pk': recipe1.pk})
    response = api_client.post(url)
    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.parametrize(
    'name',
    ('api:recipes-shopping-cart', 'api:recipes-favorite')
)
@pytest.mark.django_db
def test_remove_recipe_for_auth(api_client, user2, recipe2, name):
    user2.favourites.create(recipe=recipe2)
    user2.shopping_carts.create(recipe=recipe2)
    token = Token.objects.create(user=user2)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse(name, kwargs={'pk': recipe2.pk})
    response = api_client.delete(url)
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.django_db
def test_subscribe_to_user(user1, user2, api_client):
    token = Token.objects.create(user=user2)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse('api:users-subscribe', kwargs={'id': user1.id})
    response = api_client.post(url)
    assert response.status_code == HTTPStatus.CREATED
    assert response.data['id'] == user1.id
    assert response.data['is_subscribed'] is True


@pytest.mark.django_db
def test_unsubscribe_from_user(api_client, user1, user2):
    user1.follower.create(following=user2)
    token = Token.objects.create(user=user1)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse('api:users-subscribe', kwargs={'id': user2.id})
    response = api_client.delete(url)
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.django_db
def test_download_cart_for_auth(api_client, user1, recipe1):
    user1.shopping_carts.create(recipe=recipe1)
    token = Token.objects.create(user=user1)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse('api:recipes-download-shopping-cart')
    response = api_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'Список покупок' in response.content.decode('utf-8')
