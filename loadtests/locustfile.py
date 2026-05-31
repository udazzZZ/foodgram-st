from random import randint

from locust import HttpUser, between, task


DEFAULT_HEADERS = {"Host": "foodgram.localhost.ru"}


class FoodgramReadOnlyUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(5)
    def recipes(self):
        self.client.get(
            "/api/recipes/?page=1&limit=6",
            headers=DEFAULT_HEADERS,
            name="/api/recipes/",
        )

    @task(3)
    def ingredients(self):
        self.client.get(
            "/api/ingredients/",
            headers=DEFAULT_HEADERS,
            name="/api/ingredients/",
        )

    @task(2)
    def users(self):
        self.client.get(
            "/api/users/?page=1&limit=6",
            headers=DEFAULT_HEADERS,
            name="/api/users/",
        )

    @task(1)
    def recipe_detail(self):
        recipe_id = randint(1, 20)
        self.client.get(
            f"/api/recipes/{recipe_id}/",
            headers=DEFAULT_HEADERS,
            name="/api/recipes/[id]/",
        )
