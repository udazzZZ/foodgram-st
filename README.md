# Foodgram - Сервис рецептов

## Запуск проекта

### Требования для запуска с Docker

-   Docker
-   Docker Compose

### 1. Клонирование репозитория

```bash
git clone https://github.com/udazzZZ/foodgram-st.git
cd foodgram-st
```

### 2. Переменные окружения

В папке infra переименовать .env.example в .env

### 3. Запуск контейнеров

Находясь в главной папке проекта выполнить:

```bash
docker-compose up --build
```

### 4. Заполнение бд тестовыми данными

После запуска контейнеров в новом окне терминала, находясь в главной папке проекта, выполнить последовательно:

```bash
docker exec -it backend python manage.py loaddata data/ingredients.json
```

```bash
docker exec -it backend python manage.py loaddata data/fixture.json
```
