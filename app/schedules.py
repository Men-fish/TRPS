"""
API эндпоинты для работы с расписанием тренеров
"""
from flask import Blueprint, request, jsonify
from app.models import Schedule, Trainer
from app.validators import validate_time, validate_day_of_week, validate_required_fields

bp = Blueprint('schedules', __name__, url_prefix='/schedules')


@bp.route('/trainer/<int:trainer_id>', methods=['GET'])
def get_trainer_schedule(trainer_id):
    """
    Получить расписание работы тренера.
    
    GET /schedules/trainer/<trainer_id>
    
    Returns:
        JSON с расписанием тренера
    """
    # Проверяем, что тренер существует
    trainer = Trainer.get_by_id(trainer_id)
    if not trainer:
        return jsonify({
            'error': 'Not Found',
            'message': 'Тренер не найден'
        }), 404
    
    # Получаем расписание
    schedules = Schedule.get_by_trainer(trainer_id)
    
    # Форматируем результат с названиями дней недели
    formatted_schedules = []
    for schedule in schedules:
        formatted_schedules.append({
            'id': schedule['id'],
            'day_of_week': schedule['day_of_week'],
            'day_name': Schedule.DAYS_OF_WEEK.get(schedule['day_of_week'], 'Неизвестно'),
            'start_time': schedule['start_time'],
            'end_time': schedule['end_time'],
            'is_active': bool(schedule['is_active']),
            'created_at': schedule['created_at'],
            'updated_at': schedule.get('updated_at')
        })
    
    return jsonify({
        'trainer': {
            'id': trainer['id'],
            'full_name': trainer['full_name'],
            'specialization': trainer['specialization']
        },
        'schedules': formatted_schedules,
        'count': len(formatted_schedules)
    }), 200


@bp.route('', methods=['POST'])
def create_schedule():
    """
    Создать новую запись расписания для тренера.
    
    POST /schedules
    Body (JSON):
    {
        "trainer_id": 1,
        "day_of_week": 0,
        "start_time": "09:00",
        "end_time": "18:00",
        "is_active": true
    }
    
    Returns:
        JSON с созданным расписанием
    """
    # Получаем данные из запроса
    data = request.get_json(force=True, silent=True)
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Запрос должен быть в формате JSON'
        }), 400
    
    # Проверка обязательных полей
    required_fields = ['trainer_id', 'day_of_week', 'start_time', 'end_time']
    is_valid, missing_fields = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
        }), 400
    
    trainer_id = data.get('trainer_id')
    day_of_week = data.get('day_of_week')
    start_time = data.get('start_time', '').strip()
    end_time = data.get('end_time', '').strip()
    is_active = data.get('is_active', True)
    
    # Валидация trainer_id
    try:
        trainer_id = int(trainer_id)
    except (ValueError, TypeError):
        return jsonify({
            'error': 'Validation Error',
            'message': 'trainer_id должен быть числом'
        }), 400
    
    # Проверка существования тренера
    trainer = Trainer.get_by_id(trainer_id)
    if not trainer:
        return jsonify({
            'error': 'Not Found',
            'message': 'Тренер не найден'
        }), 404
    
    # Валидация дня недели
    is_valid, error, day_int = validate_day_of_week(day_of_week)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': error
        }), 400
    
    # Валидация времени начала
    is_valid, error = validate_time(start_time)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': f'start_time: {error}'
        }), 400
    
    # Валидация времени окончания
    is_valid, error = validate_time(end_time)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': f'end_time: {error}'
        }), 400
    
    # Проверка, что время окончания больше времени начала
    start_hours, start_minutes = map(int, start_time.split(':'))
    end_hours, end_minutes = map(int, end_time.split(':'))
    start_total = start_hours * 60 + start_minutes
    end_total = end_hours * 60 + end_minutes
    
    if end_total <= start_total:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Время окончания должно быть больше времени начала'
        }), 400
    
    # Проверка, не существует ли уже расписание на этот день
    existing = Schedule.get_by_trainer_and_day(trainer_id, day_int)
    if existing:
        return jsonify({
            'error': 'Conflict',
            'message': f'Расписание на {Schedule.DAYS_OF_WEEK.get(day_int)} уже существует. Используйте PUT для обновления.'
        }), 409
    
    # Создаем расписание
    schedule = Schedule.create(trainer_id, day_int, start_time, end_time, is_active)
    
    if not schedule:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Ошибка при создании расписания'
        }), 500
    
    return jsonify({
        'message': 'Расписание успешно создано',
        'schedule': {
            'id': schedule['id'],
            'trainer_id': schedule['trainer_id'],
            'day_of_week': schedule['day_of_week'],
            'day_name': Schedule.DAYS_OF_WEEK.get(schedule['day_of_week'], 'Неизвестно'),
            'start_time': schedule['start_time'],
            'end_time': schedule['end_time'],
            'is_active': bool(schedule['is_active']),
            'created_at': schedule['created_at']
        }
    }), 201


@bp.route('/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """
    Обновить расписание.
    
    PUT /schedules/<id>
    Body (JSON):
    {
        "start_time": "10:00",  // опционально
        "end_time": "19:00",    // опционально
        "is_active": false      // опционально
    }
    
    Returns:
        JSON с обновленным расписанием
    """
    # Проверяем, что расписание существует
    schedule = Schedule.get_by_id(schedule_id)
    if not schedule:
        return jsonify({
            'error': 'Not Found',
            'message': 'Расписание не найдено'
        }), 404
    
    # Получаем данные из запроса
    data = request.get_json(force=True, silent=True)
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Запрос должен быть в формате JSON'
        }), 400
    
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    is_active = data.get('is_active')
    
    # Валидация времени начала, если передано
    if start_time is not None:
        start_time = start_time.strip()
        is_valid, error = validate_time(start_time)
        if not is_valid:
            return jsonify({
                'error': 'Validation Error',
                'message': f'start_time: {error}'
            }), 400
    
    # Валидация времени окончания, если передано
    if end_time is not None:
        end_time = end_time.strip()
        is_valid, error = validate_time(end_time)
        if not is_valid:
            return jsonify({
                'error': 'Validation Error',
                'message': f'end_time: {error}'
            }), 400
    
    # Проверка, что время окончания больше времени начала
    # Используем переданные значения или текущие из БД
    check_start = start_time if start_time is not None else schedule['start_time']
    check_end = end_time if end_time is not None else schedule['end_time']
    
    start_hours, start_minutes = map(int, check_start.split(':'))
    end_hours, end_minutes = map(int, check_end.split(':'))
    start_total = start_hours * 60 + start_minutes
    end_total = end_hours * 60 + end_minutes
    
    if end_total <= start_total:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Время окончания должно быть больше времени начала'
        }), 400
    
    # Обновляем расписание
    updated_schedule = Schedule.update(
        schedule_id,
        start_time=start_time,
        end_time=end_time,
        is_active=is_active
    )
    
    if not updated_schedule:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Ошибка при обновлении расписания'
        }), 500
    
    return jsonify({
        'message': 'Расписание успешно обновлено',
        'schedule': {
            'id': updated_schedule['id'],
            'trainer_id': updated_schedule['trainer_id'],
            'day_of_week': updated_schedule['day_of_week'],
            'day_name': Schedule.DAYS_OF_WEEK.get(updated_schedule['day_of_week'], 'Неизвестно'),
            'start_time': updated_schedule['start_time'],
            'end_time': updated_schedule['end_time'],
            'is_active': bool(updated_schedule['is_active']),
            'created_at': updated_schedule['created_at'],
            'updated_at': updated_schedule.get('updated_at')
        }
    }), 200


@bp.route('/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """
    Удалить расписание.
    
    DELETE /schedules/<id>
    
    Returns:
        JSON с подтверждением удаления
    """
    # Проверяем, что расписание существует
    schedule = Schedule.get_by_id(schedule_id)
    if not schedule:
        return jsonify({
            'error': 'Not Found',
            'message': 'Расписание не найдено'
        }), 404
    
    # Удаляем расписание
    deleted = Schedule.delete(schedule_id)
    
    if not deleted:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Ошибка при удалении расписания'
        }), 500
    
    return jsonify({
        'message': 'Расписание успешно удалено'
    }), 200

