"""
Модуль аутентификации пользователей
"""
from functools import wraps
from flask import Blueprint, request, jsonify, session
from app.models import User
from app.validators import (
    validate_email, validate_password, validate_full_name,
    validate_passport_data, validate_required_fields
)
from app.csrf import get_csrf_token
from flask import current_app


def require_auth(f):
    """
    Декоратор для проверки авторизации пользователя.
    
    Usage:
        @require_auth
        @bp.route('/protected', methods=['GET'])
        def protected_route():
            user_id = session.get('user_id')
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Требуется авторизация'
            }), 401
        
        # Проверяем, что пользователь существует
        user = User.get_by_id(user_id)
        if not user:
            session.clear()
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Пользователь не найден'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя.
    
    POST /auth/register
    Body (JSON):
    {
        "full_name": "Иванов Иван Иванович",
        "email": "ivan@example.com",
        "password": "password123",
        "passport_data": "1234 567890"
    }
    
    Returns:
        JSON с данными пользователя или ошибкой
    """
    # Получаем данные из запроса
    # Используем force=True и silent=True для надежного получения JSON
    data = request.get_json(force=True, silent=True)
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Запрос должен быть в формате JSON'
        }), 400
    
    # Проверка обязательных полей
    required_fields = ['full_name', 'email', 'password', 'passport_data']
    is_valid, missing_fields = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
        }), 400
    
    # Валидация полей
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    passport_data = data.get('passport_data', '').strip()
    
    # Валидация ФИО
    is_valid, error = validate_full_name(full_name)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': error
        }), 400
    
    # Валидация email
    is_valid, error = validate_email(email)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': error
        }), 400
    
    # Валидация пароля
    is_valid, error = validate_password(password)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': error
        }), 400
    
    # Валидация паспортных данных
    is_valid, error = validate_passport_data(passport_data)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': error
        }), 400
    
    # Проверка, не существует ли уже пользователь с таким email
    existing_user = User.get_by_email(email)
    if existing_user:
        return jsonify({
            'error': 'Conflict',
            'message': 'Пользователь с таким email уже существует'
        }), 409
    
    # Создание пользователя
    user = User.create(full_name, email, password, passport_data)
    
    if not user:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Ошибка при создании пользователя'
        }), 500
    
    # Возвращаем данные пользователя (без пароля и паспортных данных)
    return jsonify({
        'message': 'Пользователь успешно зарегистрирован',
        'user': {
            'id': user['id'],
            'full_name': user['full_name'],
            'email': user['email'],
            'created_at': user['created_at']
        }
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """
    Авторизация пользователя.
    
    POST /auth/login
    Body (JSON):
    {
        "email": "ivan@example.com",
        "password": "password123"
    }
    
    Returns:
        JSON с данными пользователя и CSRF токеном
    """
    # Получаем данные из запроса
    # Используем force=True и silent=True для надежного получения JSON
    data = request.get_json(force=True, silent=True)
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Запрос должен быть в формате JSON'
        }), 400
    
    # Проверка обязательных полей
    required_fields = ['email', 'password']
    is_valid, missing_fields = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
        }), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Валидация email
    is_valid, error = validate_email(email)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': error
        }), 400
    
    # Валидация пароля
    is_valid, error = validate_password(password)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': error
        }), 400
    
    # Поиск пользователя
    user = User.get_by_email(email)
    
    if not user:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Неверный email или пароль'
        }), 401
    
    # Проверка пароля
    if not User.verify_password(user, password):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Неверный email или пароль'
        }), 401
    
    # Создание сессии
    session.permanent = True
    session['user_id'] = user['id']
    session['email'] = user['email']
    
    # Генерация CSRF токена
    csrf_token = get_csrf_token()
    
    # Формирование ответа
    response = jsonify({
        'message': 'Успешная авторизация',
        'user': {
            'id': user['id'],
            'full_name': user['full_name'],
            'email': user['email']
        },
        'csrf_token': csrf_token
    })
    
    # Устанавливаем CSRF токен в HTTP-only cookie
    response.set_cookie(
        'csrf_token',
        csrf_token,
        httponly=True,
        samesite='Strict',
        secure=False  # True для HTTPS в продакшене
    )
    
    return response, 200


@bp.route('/logout', methods=['POST'])
def logout():
    """
    Выход из системы.
    
    POST /auth/logout
    
    Returns:
        JSON с подтверждением выхода
    """
    session.clear()
    
    response = jsonify({
        'message': 'Успешный выход из системы'
    })
    
    # Удаляем CSRF токен из cookie
    response.set_cookie('csrf_token', '', expires=0)
    
    return response, 200


@bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Получить информацию о текущем авторизованном пользователе.
    
    GET /auth/me
    
    Returns:
        JSON с данными пользователя
    """
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Требуется авторизация'
        }), 401
    
    user = User.get_by_id(user_id)
    
    if not user:
        session.clear()
        return jsonify({
            'error': 'Not Found',
            'message': 'Пользователь не найден'
        }), 404
    
    return jsonify({
        'user': {
            'id': user['id'],
            'full_name': user['full_name'],
            'email': user['email'],
            'created_at': user['created_at']
        }
    }), 200

