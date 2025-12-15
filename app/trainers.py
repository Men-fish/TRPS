"""
Модуль для работы с тренерами
"""
from flask import Blueprint, request, jsonify
from app.models import Trainer, Review
from app.validators import validate_required_fields

bp = Blueprint('trainers', __name__, url_prefix='/trainers')


@bp.route('', methods=['GET'])
def get_trainers():
    """
    Получить список тренеров с фильтрацией.
    
    GET /trainers
    Query Parameters:
        - specialization: Фильтр по специализации (опционально)
        - search: Поиск по ФИО (опционально)
    
    Returns:
        JSON со списком тренеров
    """
    # Получаем параметры фильтрации
    specialization = request.args.get('specialization', '').strip()
    search = request.args.get('search', '').strip()
    
    # Если параметры пустые, передаем None
    specialization = specialization if specialization else None
    search = search if search else None
    
    # Получаем список тренеров
    trainers = Trainer.get_all(
        specialization=specialization,
        search=search
    )
    
    # Форматируем ответ
    trainers_list = []
    for trainer in trainers:
        trainers_list.append({
            'id': trainer['id'],
            'full_name': trainer['full_name'],
            'specialization': trainer['specialization'],
            'description': trainer['description'],
            'address': trainer.get('address'),
            'gym_name': trainer.get('gym_name'),
            'created_at': trainer['created_at']
        })
    
    return jsonify({
        'trainers': trainers_list,
        'count': len(trainers_list)
    }), 200


@bp.route('/<int:trainer_id>', methods=['GET'])
def get_trainer(trainer_id):
    """
    Получить детальную информацию о тренере.
    
    GET /trainers/<id>
    
    Returns:
        JSON с информацией о тренере и его отзывах
    """
    # Получаем тренера
    trainer = Trainer.get_by_id(trainer_id)
    
    if not trainer:
        return jsonify({
            'error': 'Not Found',
            'message': 'Тренер не найден'
        }), 404
    
    # Получаем отзывы о тренере
    reviews = Review.get_by_trainer(trainer_id)
    
    # Вычисляем среднюю оценку
    if reviews:
        avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
        reviews_count = len(reviews)
    else:
        avg_rating = 0
        reviews_count = 0
    
    # Форматируем отзывы
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
    
    # Формируем ответ
    return jsonify({
        'trainer': {
            'id': trainer['id'],
            'full_name': trainer['full_name'],
            'specialization': trainer['specialization'],
            'description': trainer['description'],
            'address': trainer.get('address'),
            'gym_name': trainer.get('gym_name'),
            'created_at': trainer['created_at'],
            'rating': {
                'average': round(avg_rating, 2),
                'count': reviews_count
            }
        },
        'reviews': reviews_list
    }), 200

