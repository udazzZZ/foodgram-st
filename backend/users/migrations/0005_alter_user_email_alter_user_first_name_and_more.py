# Generated by Django 5.2.3 on 2025-06-28 19:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Почта'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=150, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_', regex='^[\\w.@+-]+\\Z'), django.core.validators.MinLengthValidator(limit_value=4, message='Имя пользователя должно быть не короче 4 символов'), django.core.validators.MaxLengthValidator(limit_value=30, message='Имя пользователя должно быть не длиннее 30 символов')], verbose_name='Имя пользователя'),
        ),
    ]
