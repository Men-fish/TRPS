# Инструкция по запуску и тестированию проекта

## 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 2. Запуск приложения

```bash
python app.py
```

Приложение будет доступно по адресу: `http://localhost:5000`

База данных `trainers.db` создастся автоматически при первом запуске.

## 3. Подготовка тестовых данных

Перед тестированием API тренеров рекомендуется добавить тестовых тренеров:

```bash
python add_test_trainers.py
```

Это добавит 6 тестовых тренеров разных специализаций в базу данных.

## 4. Тестирование API

### Вариант 1: Автоматическое тестирование (рекомендуется)

Запустите `test_api.py`:
```bash
python test_api.py
```

Скрипт автоматически проверит все 36 эндпоинтов:
- ✅ PASS - тест прошел успешно
- ❌ FAIL - тест не прошел

**Ожидаемый результат:** `Пройдено: 36/36`

### Вариант 2: Использование curl

#### Получить CSRF токен
```bash
curl -X GET http://localhost:5000/api/csrf-token
```

**Ответ:**
```json
{
  "csrf_token": "..."
}
```

#### Регистрация пользователя

**cURL команда:**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Иванов Иван Иванович",
    "email": "ivan@example.com",
    "password": "password123",
    "passport_data": "1234 567890"
  }'
```

**Успешный ответ (201):**
```json
{
  "message": "Пользователь успешно зарегистрирован",
  "user": {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "email": "ivan@example.com",
    "created_at": "2025-12-07 16:00:00"
  }
}
```

#### Авторизация
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "ivan@example.com",
    "password": "password123"
  }'
```

**Успешный ответ (200):**
```json
{
  "message": "Успешная авторизация",
  "user": {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "email": "ivan@example.com"
  },
  "csrf_token": "..."
}
```

**Важно:** Сохраните `csrf_token` для последующих запросов.

#### Получить информацию о текущем пользователе
```bash
curl -X GET http://localhost:5000/auth/me \
  -b cookies.txt
```

#### Выход
```bash
curl -X POST http://localhost:5000/auth/logout \
  -b cookies.txt
```

### Вариант 3: Тестирование тренеров

#### Получить список всех тренеров
```bash
curl -X GET http://localhost:5000/trainers
```

**Ответ:**
```json
{
  "trainers": [...],
  "count": 6
}
```

#### Фильтрация по специализации
```bash
curl -X GET "http://localhost:5000/trainers?specialization=Фитнес"
```

#### Поиск по специализации
```bash
curl -X GET "http://localhost:5000/trainers?specialization=Йога"
```

#### Детали тренера
```bash
curl -X GET http://localhost:5000/trainers/1
```

**Пример ответа:**
```json
{
  "trainer": {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "specialization": "Фитнес",
    "description": "Опытный фитнес-тренер...",
    "address": "г. Москва, ул. Ленина, д. 10",
    "gym_name": "Фитнес-клуб \"Сила\"",
    "created_at": "2025-12-07 13:00:00",
    "rating": {
      "average": 4.5,
      "count": 10
    }
  },
  "reviews": [
    {
      "id": 1,
      "user_name": "Петров Петр",
      "text": "Отличный тренер!",
      "rating": 5,
      "created_at": "2025-12-07 14:00:00",
      "updated_at": null
    }
  ]
}
```

**Ошибки:**
- `404 Not Found` - если тренер с указанным ID не найден

### Вариант 4: Записи на тренировки

#### Получить историю записей пользователя
```bash
curl -X GET http://localhost:5000/records \
  -b cookies.txt
```

**С фильтрацией по статусу:**
```bash
curl -X GET "http://localhost:5000/records?status=pending" \
  -b cookies.txt
```

**Пример ответа:**
```json
{
  "records": [
    {
      "id": 1,
      "trainer": {
        "id": 1,
        "full_name": "Иванов Иван Иванович",
        "specialization": "Фитнес",
        "address": "г. Москва, ул. Ленина, д. 10",
        "gym_name": "Фитнес-клуб \"Сила\""
      },
      "datetime": "2025-12-10 14:00:00",
      "status": "pending",
      "created_at": "2025-12-07 15:00:00"
    }
  ],
  "count": 1
}
```

**Ошибки:**
- `401 Unauthorized` - если пользователь не авторизован

#### Создать запись на тренировку
```bash
curl -X POST http://localhost:5000/records \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <csrf_token>" \
  -b cookies.txt \
  -d '{
    "trainer_id": 1,
    "datetime": "2025-12-15 14:00:00"
  }'
```

**Пример ответа (201):**
```json
{
  "message": "Запись успешно создана",
  "record": {
    "id": 1,
    "trainer": {
      "id": 1,
      "full_name": "Иванов Иван Иванович",
      "specialization": "Фитнес"
    },
    "datetime": "2025-12-15 14:00:00",
    "status": "pending",
    "created_at": "2025-12-07 15:00:00"
  }
}
```

**Ошибки:**
- `400 Bad Request` - неверный формат данных или отсутствуют обязательные поля
- `401 Unauthorized` - если пользователь не авторизован
- `403 Forbidden` - если CSRF токен невалиден
- `404 Not Found` - если тренер не найден
- `400 Validation Error` - ошибка валидации даты/времени (дата должна быть в будущем)

#### Изменить запись
```bash
curl -X PUT http://localhost:5000/records/1 \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <csrf_token>" \
  -b cookies.txt \
  -d '{
    "datetime": "2025-12-15 15:00:00",
    "status": "confirmed"
  }'
```

**Ошибки:**
- `401 Unauthorized` - если пользователь не авторизован
- `403 Forbidden` - если CSRF токен невалиден или запись не принадлежит пользователю
- `404 Not Found` - если запись не найдена
- `400 Validation Error` - неверный статус (допустимые: pending, confirmed, cancelled, completed)

#### Отменить запись
```bash
curl -X DELETE http://localhost:5000/records/1 \
  -H "X-CSRF-Token: <csrf_token>" \
  -b cookies.txt
```

**Пример ответа (200):**
```json
{
  "message": "Запись успешно отменена",
  "record": {
    "id": 1,
    "status": "cancelled"
  }
}
```

**Ошибки:**
- `401 Unauthorized` - если пользователь не авторизован
- `403 Forbidden` - если CSRF токен невалиден или запись не принадлежит пользователю
- `404 Not Found` - если запись не найдена

### Вариант 5: Отзывы

#### Получить список отзывов о тренере
```bash
curl -X GET http://localhost:5000/reviews/1
```

**Пример ответа:**
```json
{
  "trainer": {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "specialization": "Фитнес",
    "address": "г. Москва, ул. Ленина, д. 10",
    "gym_name": "Фитнес-клуб \"Сила\""
  },
  "reviews": [
    {
      "id": 1,
      "user_name": "Петров Петр",
      "text": "Отличный тренер!",
      "rating": 5,
      "created_at": "2025-12-07 14:00:00",
      "updated_at": null
    }
  ],
  "count": 1
}
```

**Ошибки:**
- `404 Not Found` - если тренер не найден

#### Создать отзыв о тренере
```bash
curl -X POST http://localhost:5000/reviews \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <csrf_token>" \
  -b cookies.txt \
  -d '{
    "trainer_id": 1,
    "text": "Отличный тренер! Очень рекомендую.",
    "rating": 5
  }'
```

**Пример ответа (201):**
```json
{
  "message": "Отзыв успешно создан",
  "review": {
    "id": 1,
    "user_name": "Иванов Иван Иванович",
    "trainer_id": 1,
    "text": "Отличный тренер! Очень рекомендую.",
    "rating": 5,
    "created_at": "2025-12-07 15:00:00"
  }
}
```

**Ошибки:**
- `400 Bad Request` - неверный формат данных или отсутствуют обязательные поля
- `401 Unauthorized` - если пользователь не авторизован
- `403 Forbidden` - если CSRF токен невалиден
- `404 Not Found` - если тренер не найден
- `400 Validation Error` - ошибка валидации (оценка должна быть 1-5, текст не пустой, максимум 2000 символов)
- `409 Conflict` - если пользователь уже оставил отзыв этому тренеру

#### Редактировать отзыв
```bash
curl -X PUT http://localhost:5000/reviews/1 \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <csrf_token>" \
  -b cookies.txt \
  -d '{
    "text": "Обновленный текст отзыва",
    "rating": 4
  }'
```

**Пример ответа (200):**
```json
{
  "message": "Отзыв успешно обновлен",
  "review": {
    "id": 1,
    "user_name": "Иванов Иван Иванович",
    "trainer_id": 1,
    "trainer_name": "Иванов Иван Иванович",
    "text": "Обновленный текст отзыва",
    "rating": 4,
    "created_at": "2025-12-07 15:00:00",
    "updated_at": "2025-12-07 16:00:00"
  }
}
```

**Ошибки:**
- `401 Unauthorized` - если пользователь не авторизован
- `403 Forbidden` - если CSRF токен невалиден или отзыв не принадлежит пользователю
- `404 Not Found` - если отзыв не найден
- `400 Validation Error` - ошибка валидации данных

## 5. Проверка базы данных

Для просмотра данных в SQLite можно использовать:

```bash
sqlite3 trainers.db
```

Затем выполните SQL запросы:
```sql
.tables
SELECT * FROM users;
SELECT * FROM trainers;
SELECT * FROM records;
SELECT * FROM reviews;
```

## 6. Ожидаемые ответы

### Успешная регистрация (201):
```json
{
  "message": "Пользователь успешно зарегистрирован",
  "user": {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "email": "ivan@example.com",
    "created_at": "2025-12-07 16:00:00"
  }
}
```

### Успешная авторизация (200):
```json
{
  "message": "Успешная авторизация",
  "user": {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "email": "ivan@example.com"
  },
  "csrf_token": "..."
}
```

### Ошибка валидации (400):
```json
{
  "error": "Validation Error",
  "message": "Email обязателен для заполнения"
}
```

### Неавторизован (401):
```json
{
  "error": "Unauthorized",
  "message": "Требуется авторизация"
}
```

### Нет прав доступа (403):
```json
{
  "error": "Forbidden",
  "message": "Недостаточно прав для выполнения операции"
}
```

### Ресурс не найден (404):
```json
{
  "error": "Not Found",
  "message": "Тренер не найден"
}
```

### Конфликт (409):
```json
{
  "error": "Conflict",
  "message": "Пользователь с таким email уже существует"
}
```

## 7. Полный список эндпоинтов

### Аутентификация
- `GET /api/csrf-token` - Получение CSRF токена
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Авторизация
- `GET /auth/me` - Информация о текущем пользователе (требует авторизацию)
- `POST /auth/logout` - Выход из системы (требует авторизацию)

### Тренеры
- `GET /trainers` - Список тренеров (с фильтрацией и поиском)
- `GET /trainers/<id>` - Детальная информация о тренере

### Записи
- `GET /records` - История записей пользователя (требует авторизацию)
- `POST /records` - Создание записи (требует авторизацию + CSRF)
- `PUT /records/<id>` - Изменение записи (требует авторизацию + CSRF)
- `DELETE /records/<id>` - Отмена записи (требует авторизацию + CSRF)

### Отзывы
- `GET /reviews/<trainer_id>` - Список отзывов о тренере
- `POST /reviews` - Создание отзыва (требует авторизацию + CSRF)
- `PUT /reviews/<id>` - Редактирование отзыва (требует авторизацию + CSRF)

## 8. Статусы записей

- `pending` - Ожидает подтверждения
- `confirmed` - Подтверждена
- `cancelled` - Отменена
- `completed` - Завершена

## 9. Валидация данных

### Email
- Формат: стандартный формат email
- Максимальная длина: 255 символов
- Уникальность: email должен быть уникальным

### Пароль
- Минимальная длина: 6 символов
- Максимальная длина: 128 символов

### ФИО
- Минимальная длина: 2 символа
- Максимальная длина: 200 символов
- Допустимые символы: буквы, пробелы, дефисы

### Дата и время
- Формат: `YYYY-MM-DD HH:MM:SS` или `YYYY-MM-DDTHH:MM:SS`
- Обязательно: дата должна быть в будущем

### Оценка (Rating)
- Диапазон: 1-5
- Тип: целое число

### Текст отзыва
- Минимальная длина: не пустой
- Максимальная длина: 2000 символов

### Адрес тренера (address)
- Поле опциональное (может быть `None`)
- Минимальная длина: 5 символов (если указан)
- Максимальная длина: 500 символов
- Допустимые символы: буквы, цифры, пробелы, дефисы, точки, запятые, скобки, слэши

### Название зала (gym_name)
- Поле опциональное (может быть `None`)
- Минимальная длина: 2 символа (если указано)
- Максимальная длина: 200 символов
- Допустимые символы: буквы, цифры, пробелы, дефисы, кавычки
