# Фудграм

## О проекте

"Фудграм" - веб-сайт, где пользователи смогут публиковать свои рецепты,
добавлять понравившиеся рецепты в избранное и подписываться на других авторов.
Зарегистрированным пользователям доступна функция "Список покупок",
которая формирует набор продуктов, необходимых для приготовления выбранных блюд.

## Технологии

* Django
* PostgreSQL
* React
* Nginx
* Docker
* GitHub Actions

## Запуск проекта в режиме разработки

1. Клонируйте репозиторий и перейдите в папку backend:

    ```bash
    git clone https://github.com/Ivan0-O/foodgram-st.git
    cd foodgram-st/backend
    ```

2. Создайте и активируйте виртуальное окружение (Linux):

    ```bash
    python -m venv env
    source ./env/bin/activate
    ```

3. Обновите pip и установите зависимости из `requirements.txt`:

    ```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

4. Примените миграции:

    ```bash
    python manage.py migrate
    ```

5. Создайте суперпользователя:

    ```bash
    python manage.py createsuperuser
    ```

6. Соберите статические файлы:

    ```bash
    python manage.py collectstatic --no-input
    ```

7. Запустите сервер:

    ```bash
    python manage.py runserver
    ```

8. Установите настройки для разработки в файле `settings.py`:

    ```python
    DEBUG = TRUE

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    ```

После этих шагов backend будет доступен и можно запускать тесты API.
Для продакшена рекомендуется изменить настройки по умолчанию.

## Запуск проекта в продакшн (прокси, бэкенд, фронтенд, база данных)

1. Установите Docker и Docker Compose согласно официальной документации.

2. Клонируйте репозиторий (если ещё не сделали):

    ```bash
    git clone https://github.com/GrigThe/foodgram-st.git
    ```

3. В корне проекта создайте файл `.env` и заполните параметры.
Пример файла окружения находится в `.env.example`:

4. Соберите и поднимите контейнеры:

    ```bash
    docker compose up -d --build
    ```

5. Примените миграции в контейнере backend:

    ```bash
    docker-compose exec backend python manage.py migrate
    ```

6. Создайте суперпользователя внутри контейнера:

    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```

7. (Опционально) Загрузите тестовые данные из фикстуры:

    ```bash
    docker-compose exec backend python manage.py loaddata initial_data.json
    ```

8. Соберите статические файлы в контейнере:

    ```bash
    docker-compose exec backend python manage.py collectstatic --no-input
    ```

После этого проект будет полностью развёрнут в контейнерах и готов к использованию
по стандартному порту 80 на локальном хосте (127.0.0.1).
