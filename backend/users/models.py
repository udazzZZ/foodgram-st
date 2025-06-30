from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    RegexValidator,
    MinLengthValidator,
    MaxLengthValidator
)


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Почта'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Имя пользователя может содержать только буквы, цифры '
                    'и символы @/./+/-/_')
            ),
            MinLengthValidator(
                limit_value=4,
                message='Имя пользователя должно быть не короче 4 символов'
            ),
            MaxLengthValidator(
                limit_value=30,
                message='Имя пользователя должно быть не длиннее 30 символов'
            ),
        ],
        verbose_name='Имя пользователя'
    )

    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Фамилия'
    )

    is_subscribed = models.BooleanField(
        default=False,
        verbose_name="Подписан",
    )

    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватарка'
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
