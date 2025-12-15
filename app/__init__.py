from flask import Flask, jsonify
from config import Config
from app.database import init_app, init_db
from app.csrf import init_csrf
from app.errors import register_error_handlers

def create_app(config_class=Config):
    """Фабрика приложения Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация базы данных
    init_app(app)
    
    # Инициализация CSRF защиты
    init_csrf(app)
    
    # Регистрация обработчиков ошибок
    register_error_handlers(app)
    
    # Регистрация blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.trainers import bp as trainers_bp
    app.register_blueprint(trainers_bp)
    
    from app.records import bp as records_bp
    app.register_blueprint(records_bp)
    
    from app.reviews import bp as reviews_bp
    app.register_blueprint(reviews_bp)
    
    from app.schedules import bp as schedules_bp
    app.register_blueprint(schedules_bp)
    
    # Исключаем эндпоинты аутентификации из CSRF проверки Flask-WTF
    from app.csrf import csrf
    if csrf:
        csrf.exempt(auth_bp)
        # Исключаем эндпоинты записей и отзывов из глобальной проверки Flask-WTF
        # Используем наш декоратор @csrf_required
        for endpoint_name in ['records.create_record', 'records.update_record', 'records.delete_record',
                               'reviews.create_review', 'reviews.update_review']:
            try:
                view_func = app.view_functions.get(endpoint_name)
                if view_func:
                    csrf.exempt(view_func)
            except:
                pass
    
    # Эндпоинт для получения CSRF токена
    @app.route('/api/csrf-token', methods=['GET'])
    def get_csrf_token():
        """Получить CSRF токен для текущей сессии"""
        from app.csrf import get_csrf_token
        from flask import make_response
        token = get_csrf_token()
        response = make_response(jsonify({'csrf_token': token}))
        # Устанавливаем токен в cookie для удобства
        response.set_cookie('csrf_token', token, httponly=True, samesite='Strict')
        return response
    
    # Создание таблиц при первом запуске
    with app.app_context():
        init_db()
    
    return app

