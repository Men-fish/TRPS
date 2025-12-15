"""
Обработка ошибок приложения
"""
from flask import jsonify, request

def register_error_handlers(app):
    """
    Зарегистрировать обработчики ошибок для приложения.
    
    Args:
        app: Flask приложение
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Обработка ошибки 400 - неверный запрос"""
        return jsonify({
            'error': 'Bad Request',
            'message': 'Неверный формат запроса или отсутствуют обязательные поля',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Обработка ошибки 401 - неавторизован"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Требуется авторизация',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Обработка ошибки 403 - запрещено"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'Недостаточно прав для выполнения операции',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Обработка ошибки 404 - не найдено"""
        return jsonify({
            'error': 'Not Found',
            'message': 'Запрашиваемый ресурс не найден',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Обработка ошибки 500 - внутренняя ошибка сервера"""
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Произошла внутренняя ошибка сервера',
            'status_code': 500
        }), 500
    
    @app.errorhandler(409)
    def conflict(error):
        """Обработка ошибки 409 - конфликт"""
        return jsonify({
            'error': 'Conflict',
            'message': 'Конфликт данных (например, дубликат записи)',
            'status_code': 409
        }), 409
    
    @app.errorhandler(422)
    def validation_error(error):
        """Обработка ошибки 422 - ошибка валидации"""
        return jsonify({
            'error': 'Validation Error',
            'message': 'Ошибка валидации данных',
            'status_code': 422
        }), 422

