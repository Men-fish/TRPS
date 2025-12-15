"""
Модуль для CSRF-защиты
Использует Flask-WTF для генерации и проверки CSRF токенов
"""
from flask import request, jsonify, session, make_response, current_app
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf
from functools import wraps

# Глобальный объект CSRF для доступа из других модулей
csrf = None


def init_csrf(app):
    """
    Инициализировать CSRF защиту для приложения.
    
    Args:
        app: Flask приложение
        
    Returns:
        CSRFProtect: Объект CSRF защиты
    """
    global csrf
    csrf = CSRFProtect(app)
    return csrf


def get_csrf_token():
    """
    Получить CSRF токен для текущей сессии.
    
    Returns:
        str: CSRF токен
    """
    return generate_csrf()


def verify_csrf_token():
    """
    Проверить CSRF токен из запроса.
    
    Returns:
        bool: True если токен валиден, False иначе
    """
    try:
        # Получаем токен из заголовка, формы или JSON
        token = request.headers.get('X-CSRF-Token')
        
        if not token:
            # Пробуем получить из формы
            token = request.form.get('csrf_token')
        
        if not token:
            # Пробуем получить из JSON (даже если Content-Type не установлен)
            try:
                json_data = request.get_json(force=True, silent=True)
                if json_data:
                    token = json_data.get('csrf_token')
            except:
                pass
        
        if not token:
            return False
        
        try:
            validate_csrf(token)
            return True
        except Exception:
            return False
    except Exception:
        return False


def csrf_required(f):
    """
    Декоратор для защиты роутов от CSRF атак.
    Проверяет CSRF токен для POST, PUT, DELETE запросов.
    
    Usage:
        @csrf_required
        @app.route('/api/endpoint', methods=['POST'])
        def my_endpoint():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Проверяем только изменяющие методы
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            if not verify_csrf_token():
                return jsonify({
                    'error': 'CSRF token missing or invalid',
                    'message': 'Требуется валидный CSRF токен'
                }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def exempt_csrf(f):
    """
    Декоратор для исключения роута из CSRF проверки.
    Используется для публичных эндпоинтов (например, регистрация, логин).
    
    Usage:
        @exempt_csrf
        @app.route('/public', methods=['POST'])
        def public_endpoint():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    decorated_function.csrf_exempt = True
    return decorated_function

