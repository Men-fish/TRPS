"""
Модуль для работы с отзывами
"""
from flask import Blueprint, request, jsonify, session
from app.models import Review, Trainer, User
from app.auth import require_auth
from app.csrf import csrf_required
from app.validators import validate_rating, validate_required_fields

bp = Blueprint('reviews', __name__, url_prefix='/reviews')


@bp.route('/<int:trainer_id>', methods=['GET'])
def get_reviews(trainer_id):
    """
    Получить список отзывов о тренере.
    
    GET /reviews/<trainer_id>
    
    Returns:
        JSON со списком отзывов о тренере
    """
    # Проверяем, что тренер существует
    trainer = Trainer.get_by_id(trainer_id)
    
    if not trainer:
        return jsonify({
            'error': 'Not Found',
            'message': 'Тренер не найден'
        }), 404
    
    # Получаем отзывы о тренере
    reviews = Review.get_by_trainer(trainer_id)
    
    # Форматируем ответ
    reviews_list = []
    for review in reviews:
        reviews_list.append({
            'id': review['id'],
            'user_name': review.get('user_name', 'Анонимный пользователь'),
            'text': review['text'],
            'rating': review['rating'],
            'created_at': review['created_at'],
            'updated_at': review.get('updated_at')
        })
    
    return jsonify({
        'trainer': {
            'id': trainer['id'],
            'full_name': trainer['full_name'],
            'specialization': trainer['specialization'],
            'address': trainer.get('address'),
            'gym_name': trainer.get('gym_name')
        },
        'reviews': reviews_list,
        'count': len(reviews_list)
    }), 200


@bp.route('', methods=['POST'])
@csrf_required
@require_auth
def create_review():
    """
    Создать новый отзыв о тренере.
    
    POST /reviews
    Body (JSON):
    {
        "trainer_id": 1,
        "text": "Отличный тренер!",
        "rating": 5
    }
    
    Returns:
        JSON с созданным отзывом
    """
    # Получаем данные из запроса
    data = request.get_json(force=True, silent=True)
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Запрос должен быть в формате JSON'
        }), 400
    
    # Проверка обязательных полей
    required_fields = ['trainer_id', 'text', 'rating']
    is_valid, missing_fields = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
        }), 400
    
    user_id = session.get('user_id')
    trainer_id = data.get('trainer_id')
    text = data.get('text', '').strip()
    rating = data.get('rating')
    
    # Проверяем, что тренер существует
    trainer = Trainer.get_by_id(trainer_id)
    if not trainer:
        return jsonify({
            'error': 'Not Found',
            'message': 'Тренер не найден'
        }), 404
    
    # Валидация текста отзыва
    if not text:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Текст отзыва не может быть пустым'
        }), 400
    
    if len(text) > 2000:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Текст отзыва слишком длинный (максимум 2000 символов)'
        }), 400
    
    # Валидация оценки
    is_valid_rating, error_message, rating_int = validate_rating(rating)
    if not is_valid_rating:
        return jsonify({
            'error': 'Validation Error',
            'message': error_message
        }), 400
    
    # Проверяем, не оставлял ли пользователь уже отзыв этому тренеру
    existing_review = Review.get_by_user_and_trainer(user_id, trainer_id)
    if existing_review:
        return jsonify({
            'error': 'Conflict',
            'message': 'Вы уже оставили отзыв этому тренеру. Используйте PUT /reviews/<id> для редактирования.'
        }), 409
    
    # Создаем отзыв
    review = Review.create(
        user_id=user_id,
        trainer_id=trainer_id,
        text=text,
        rating=rating_int
    )
    
    if not review:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Не удалось создать отзыв'
        }), 500
    
    # Получаем информацию о пользователе
    user = User.get_by_id(user_id)
    
    return jsonify({
        'message': 'Отзыв успешно создан',
        'review': {
            'id': review['id'],
            'user_name': user['full_name'] if user else 'Анонимный пользователь',
            'trainer_id': review['trainer_id'],
            'text': review['text'],
            'rating': review['rating'],
            'created_at': review['created_at']
        }
    }), 201


@bp.route('/<int:review_id>', methods=['PUT'])
@csrf_required
@require_auth
def update_review(review_id):
    """
    Обновить существующий отзыв.
    
    PUT /reviews/<id>
    Body (JSON):
    {
        "text": "Обновленный текст отзыва",
        "rating": 4
    }
    
    Returns:
        JSON с обновленным отзывом
    """
    # Получаем данные из запроса
    data = request.get_json(force=True, silent=True)
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Запрос должен быть в формате JSON'
        }), 400
    
    user_id = session.get('user_id')
    
    # Проверяем, что отзыв существует
    review = Review.get_by_id(review_id)
    if not review:
        return jsonify({
            'error': 'Not Found',
            'message': 'Отзыв не найден'
        }), 404
    
    # Проверяем, что отзыв принадлежит текущему пользователю
    if not Review.belongs_to_user(review_id, user_id):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Вы можете редактировать только свои отзывы'
        }), 403
    
    # Получаем данные для обновления
    text = data.get('text')
    rating = data.get('rating')
    
    # Если текст передан, валидируем его
    if text is not None:
        text = text.strip()
        if not text:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Текст отзыва не может быть пустым'
            }), 400
        
        if len(text) > 2000:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Текст отзыва слишком длинный (максимум 2000 символов)'
            }), 400
    
    # Если оценка передана, валидируем её
    rating_int = None
    if rating is not None:
        is_valid_rating, error_message, rating_int = validate_rating(rating)
        if not is_valid_rating:
            return jsonify({
                'error': 'Validation Error',
                'message': error_message
            }), 400
    
    # Проверяем, что есть что обновлять
    if text is None and rating is None:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Необходимо указать text или rating для обновления'
        }), 400
    
    # Обновляем отзыв
    updated_review = Review.update(
        review_id=review_id,
        text=text if text is not None else None,
        rating=rating_int if rating_int is not None else None
    )
    
    if not updated_review:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Не удалось обновить отзыв'
        }), 500
    
    # Получаем информацию о пользователе и тренере
    user = User.get_by_id(user_id)
    trainer = Trainer.get_by_id(updated_review['trainer_id'])
    
    return jsonify({
        'message': 'Отзыв успешно обновлен',
        'review': {
            'id': updated_review['id'],
            'user_name': user['full_name'] if user else 'Анонимный пользователь',
            'trainer_id': updated_review['trainer_id'],
            'trainer_name': trainer['full_name'] if trainer else 'Тренер не найден',
            'text': updated_review['text'],
            'rating': updated_review['rating'],
            'created_at': updated_review['created_at'],
            'updated_at': updated_review.get('updated_at')
        }
    }), 200

