# Проект YaMDb

Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». Список категорий может быть расширен.
Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»).
Добавлять произведения, категории и жанры может только администратор.

## Пользовательские роли и права доступа

- Аноним — может просматривать описания произведений, читать отзывы и комментарии.
- Аутентифицированный пользователь (user) — может читать всё, как и Аноним, может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Эта роль присваивается по умолчанию каждому новому пользователю.
- Модератор (moderator) — те же права, что и у Аутентифицированного пользователя, плюс право удалять и редактировать любые отзывы и комментарии.
- Администратор (admin) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
- Суперюзер Django должен всегда обладать правами администратора, пользователя с правами admin. Даже если изменить пользовательскую роль суперюзера — это не лишит его прав администратора. Суперюзер — всегда администратор, но администратор — не обязательно суперюзер.

## Технологии

- Python 3.9.10
- Django 3.2
- Djangorestframework 3.12.4
- Simple JWT
## Запуск проекта в dev-режиме

1. Клонировать репозиторий и перейти в него в командной строке:

    ```bash
        git clone https://github.com/Vadim-Popov/api_yamdb/
    ```

2. Cоздать виртуальное окружение:

    windows

    ```bash
        python -m venv venv
    ```

    linux

    ```bash
        python3 -m venv venv
    ```

3. Активируйте виртуальное окружение

    windows

    ```bash
        source venv/Scripts/activate
    ```

    linux

    ```bash
        source venv/bin/activate
    ```

4. Установите зависимости из файла requirements.txt

    ```bash
        pip install -r requirements.txt
    ```
5. Выполнить миграции

    ```bash
        python api_yamdb/manage.py migrate
    ```

6. В папке с файлом manage.py выполните команду:

    windows

    ```bash
        python manage.py runserver
    ```

    linux

    ```bash
        python3 manage.py runserver
    ```

## Документация к проекту

Документация для API после установки доступна по адресу

```url
    http://127.0.0.1/redoc/
```

### Регистрация нового пользователя
Регистрация нового пользователя:
Права доступа: Доступно без токена.
```
POST /api/v1/auth/signup/
```

```json
{
  "email": "string",
  "username": "string"
}

```

Получение JWT-токена:

```
POST /api/v1/auth/token/
```

```json
{
  "username": "string",
  "confirmation_code": "string"
}
```

## Примеры запросов

- GET-Response: <http://127.0.0.1:8000/api/v1/titles/1/>

Request:

```J-SON
{
    "id": 1,
    "name": "Побег из Шоушенка",
    "year": 1994,
    "description": null,
    "genre": [
        {
            "name": "Драма",
            "slug": "drama"
        }
    ],
    "category": {
        "name": "Фильм",
        "slug": "movie"
    },
    "rating": 10
}
```

- GET-Response: <http://127.0.0.1:8000/api/v1/titles/1/reviews/1/>

Request:

```J-SON
{
    "id": 1,
    "author": "bingobongo",
    "title": 1,
    "text": 
        "Ставлю десять звёзд!\n...Эти голоса были чище и светлее тех,
        о которых мечтали в этом сером, убогом месте. Как будто две птички 
        влетели и своими голосами развеяли стены наших клеток, и на короткий
        миг каждый человек в Шоушенке почувствовал себя свободным.",
    "score": 10,
    "pub_date": "2023-05-05T18:06:02.054698Z"
}
```
Добавление категории:

```
Права доступа: Администратор.
POST /api/v1/categories/
```

```json
{
  "name": "string",
  "slug": "string"
}
```

Удаление категории:

```
Права доступа: Администратор.
DELETE /api/v1/categories/{slug}/
```

Добавление жанра:

```
Права доступа: Администратор.
POST /api/v1/genres/
```

```json
{
  "name": "string",
  "slug": "string"
}
```

Удаление жанра:

```
Права доступа: Администратор.
DELETE /api/v1/genres/{slug}/
```

Обновление публикации:

```
PUT /api/v1/posts/{id}/
```

```json
{
"text": "string",
"image": "string",
"group": 0
}
```

Добавление произведения:

```
Права доступа: Администратор. 
Нельзя добавлять произведения, которые еще не вышли (год выпуска не может быть больше текущего).

POST /api/v1/titles/
```

```json
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```

Добавление произведения:

```
Права доступа: Доступно без токена
GET /api/v1/titles/{titles_id}/
```

```json
{
  "id": 0,
  "name": "string",
  "year": 0,
  "rating": 0,
  "description": "string",
  "genre": [
    {
      "name": "string",
      "slug": "string"
    }
  ],
  "category": {
    "name": "string",
    "slug": "string"
  }
}
```

Частичное обновление информации о произведении:

```
Права доступа: Администратор
PATCH /api/v1/titles/{titles_id}/
```

```json
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```

Частичное обновление информации о произведении:
```
Права доступа: Администратор
DEL /api/v1/titles/{titles_id}/
```

### Работа с пользователями:

Для работы с пользователя есть ограничения для работы с ними.
Получение списка всех пользователей.

```
Права доступа: Администратор
GET /api/v1/users/ - Получение списка всех пользователей
```

Добавление пользователя:

```
Права доступа: Администратор
Поля email и username должны быть уникальными.
POST /api/v1/users/ - Добавление пользователя
```

```json
{
"username": "string",
"email": "user@example.com",
"first_name": "string",
"last_name": "string",
"bio": "string",
"role": "user"
}
```

Получение пользователя по username:

```
Права доступа: Администратор
GET /api/v1/users/{username}/ - Получение пользователя по username
```

Изменение данных пользователя по username:

```
Права доступа: Администратор
PATCH /api/v1/users/{username}/ - Изменение данных пользователя по username
```

```json
{
  "username": "string",
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "role": "user"
}
```

Удаление пользователя по username:

```
Права доступа: Администратор
DELETE /api/v1/users/{username}/ - Удаление пользователя по username
```

Получение данных своей учетной записи:

```
Права доступа: Любой авторизованный пользователь
GET /api/v1/users/me/ - Получение данных своей учетной записи
```

Изменение данных своей учетной записи:

- Права доступа: Любой авторизованный пользователь
```
PATCH /api/v1/users/me/ # Изменение данных своей учетной записи
```

## Авторы

Студенты курса "Python-разработчик" от Яндекс-Практикума:


- Алексей: (https://github.com/Salyuk163)
- Вадим: (https://github.com/Vadim-Popov)
- Дмитрий: (https://github.com/beliyd)
