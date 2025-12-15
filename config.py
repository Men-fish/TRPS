import os
from datetime import timedelta

class Config:
    """Конфигурация приложения"""
    
    # Секретный ключ для сессий и CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    
    # Путь к базе данных
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'trainers.db')
    
    # Настройки CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 час
    WTF_CSRF_CHECK_DEFAULT = False  # Отключаем глобальную проверку, используем декораторы
    WTF_CSRF_HEADERS = ['X-CSRF-Token']
    WTF_CSRF_METHODS = ['POST', 'PUT', 'DELETE', 'PATCH']
    
    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # True для HTTPS в продакшене
    
    # JSON настройки
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True

