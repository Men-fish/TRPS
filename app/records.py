"""
Модуль для работы с записями на тренировки
"""
from flask import Blueprint, request, jsonify, session
from app.models import Record, Trainer, Schedule, User
from app.auth import require_auth
from app.csrf import csrf_required
from app.validators import validate_datetime, validate_required_fields, validate_duration

bp = Blueprint('records', __name__, url_prefix='/records')


@bp.route('', methods=['GET'])
@require_auth
def get_records():
    """
    Получить историю записей текущего авторизованного пользователя.
    
    GET /records
    Query Parameters:
        - status: Фильтр по статусу (pending, confirmed, cancelled, completed) - опционально
    
    Returns:
        JSON со списком записей пользователя
    """
    user_id = session.get('user_id')
    
    # Получаем параметр фильтрации по статусу
    status = request.args.get('status', '').strip()
    status = status if status else None
    
    # Получаем записи пользователя
    records = Record.get_by_user(user_id, status=status)
    
    # Форматируем ответ с информацией о тренерах
    records_list = []
    for record in records:
        # Получаем информацию о тренере
        trainer = Trainer.get_by_id(record['trainer_id'])
        
        records_list.append({
            'id': record['id'],
            'trainer': {
                'id': trainer['id'] if trainer else None,
                'full_name': trainer['full_name'] if trainer else 'Тренер не найден',
                'specialization': trainer['specialization'] if trainer else None,
                'address': trainer.get('address') if trainer else None,
                'gym_name': trainer.get('gym_name') if trainer else None
            } if trainer else None,
            'datetime': record['datetime'],
            'duration': record.get('duration', 60),
            'status': record['status'],
            'created_at': record['created_at']
        })
    
    return jsonify({
        'records': records_list,
        'count': len(records_list)
    }), 200


@bp.route('', methods=['POST'])
@csrf_required
@require_auth
def create_record():
    """
    Создать новую запись на тренировку.
    
    POST /records
    Body (JSON):
    {
        "trainer_id": 1,
        "datetime": "2025-12-10 14:00:00",
        "duration": 60  // опционально, по умолчанию 60 минут
    }
    
    Returns:
        JSON с созданной записью
    """
    # Получаем данные из запроса
    data = request.get_json(force=True, silent=True)
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Запрос должен быть в формате JSON'
        }), 400
    
    # Проверка обязательных полей
    required_fields = ['trainer_id', 'datetime']
    is_valid, missing_fields = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
        }), 400
    
    user_id = session.get('user_id')
    trainer_id = data.get('trainer_id')
    datetime_str = data.get('datetime', '').strip()
    duration = data.get('duration', 60)  # По умолчанию 60 минут
    
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
    
    # Валидация даты и времени
    is_valid, error, datetime_obj = validate_datetime(datetime_str)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': error
        }), 400
    
    # Валидация длительности
    is_valid, error, duration_int = validate_duration(duration)
    if not is_valid:
        return jsonify({
            'error': 'Validation Error',
            'message': error
        }), 400
    
    # Форматируем дату/время в нужный формат
    datetime_formatted = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    
    # Проверка рабочего времени тренера (проверяем начало и конец тренировки)
    is_working, error_message = Schedule.is_working_time(trainer_id, datetime_obj)
    if not is_working:
        return jsonify({
            'error': 'Validation Error',
            'message': error_message
        }), 400
    
    # Проверяем, что конец тренировки тоже в рабочее время
    from datetime import timedelta
    end_datetime = datetime_obj + timedelta(minutes=duration_int)
    is_working_end, error_message_end = Schedule.is_working_time(trainer_id, end_datetime)
    if not is_working_end:
        return jsonify({
            'error': 'Validation Error',
            'message': f'Тренировка заканчивается вне рабочего времени тренера: {error_message_end}'
        }), 400
    
    # Проверка на конфликт: нельзя записаться к тренеру, если время перекрывается с существующими записями
    if Record.exists_conflicting_record(trainer_id, datetime_formatted, duration_int):
        return jsonify({
            'error': 'Conflict',
            'message': 'На это время уже есть запись к данному тренеру (время перекрывается)'
        }), 409
    
    # Создаем запись
    record = Record.create(user_id, trainer_id, datetime_formatted, duration_int)
    
    if not record:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Ошибка при создании записи'
        }), 500
    
    # Получаем информацию о тренере для ответа
    trainer = Trainer.get_by_id(trainer_id)
    
    return jsonify({
        'message': 'Запись успешно создана',
        'record': {
            'id': record['id'],
            'trainer': {
                'id': trainer['id'],
                'full_name': trainer['full_name'],
                'specialization': trainer['specialization'],
                'address': trainer.get('address'),
                'gym_name': trainer.get('gym_name')
            },
            'datetime': record['datetime'],
            'duration': record.get('duration', 60),
            'status': record['status'],
            'created_at': record['created_at']
        }
    }), 201


@bp.route('/<int:record_id>', methods=['PUT'])
@csrf_required
@require_auth
def update_record(record_id):
    """
    Изменить запись на тренировку.
    
    PUT /records/<id>
    Body (JSON):
    {
        "datetime": "2025-12-10 15:00:00",  // опционально
        "duration": 90,  // опционально, длительность в минутах
        "status": "confirmed"  // опционально
    }
    
    Returns:
        JSON с обновленной записью
    """
    user_id = session.get('user_id')
    
    # Проверяем, что запись существует и принадлежит пользователю
    record = Record.get_by_id(record_id)
    
    if not record:
        return jsonify({
            'error': 'Not Found',
            'message': 'Запись не найдена'
        }), 404
    
    if not Record.belongs_to_user(record_id, user_id):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Недостаточно прав для изменения этой записи'
        }), 403
    
    # Получаем данные из запроса
    data = request.get_json(force=True, silent=True)
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Запрос должен быть в формате JSON'
        }), 400
    
    datetime_str = data.get('datetime', '').strip() if data.get('datetime') else None
    duration = data.get('duration')
    status = data.get('status')
    
    # Валидация статуса, если передан
    if status is not None:
        valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        if status not in valid_statuses:
            return jsonify({
                'error': 'Validation Error',
                'message': f'Неверный статус. Допустимые значения: {", ".join(valid_statuses)}'
            }), 400
    
    # Валидация длительности, если передана
    duration_int = None
    if duration is not None:
        is_valid, error, duration_int = validate_duration(duration)
        if not is_valid:
            return jsonify({
                'error': 'Validation Error',
                'message': error
            }), 400
    
    # Используем текущую длительность записи, если не указана новая
    current_duration = record.get('duration', 60) or 60
    duration_to_check = duration_int if duration_int is not None else current_duration
    
    # Валидация даты и времени, если передано
    datetime_formatted = None
    datetime_obj = None
    if datetime_str:
        is_valid, error, datetime_obj = validate_datetime(datetime_str)
        if not is_valid:
            return jsonify({
                'error': 'Validation Error',
                'message': error
            }), 400
        datetime_formatted = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        
        # Проверка рабочего времени тренера (начало)
        is_working, error_message = Schedule.is_working_time(record['trainer_id'], datetime_obj)
        if not is_working:
            return jsonify({
                'error': 'Validation Error',
                'message': error_message
            }), 400
        
        # Проверка рабочего времени тренера (конец)
        from datetime import timedelta
        end_datetime = datetime_obj + timedelta(minutes=duration_to_check)
        is_working_end, error_message_end = Schedule.is_working_time(record['trainer_id'], end_datetime)
        if not is_working_end:
            return jsonify({
                'error': 'Validation Error',
                'message': f'Тренировка заканчивается вне рабочего времени тренера: {error_message_end}'
            }), 400
        
        # Проверка на конфликт при изменении времени (с учетом длительности)
        if Record.exists_conflicting_record(record['trainer_id'], datetime_formatted, duration_to_check, exclude_record_id=record_id):
            return jsonify({
                'error': 'Conflict',
                'message': 'На это время уже есть запись к данному тренеру (время перекрывается)'
            }), 409
    elif duration_int is not None:
        # Если изменяется только длительность, проверяем, что конец тренировки в рабочем времени
        from datetime import datetime, timedelta
        current_datetime = datetime.strptime(record['datetime'], '%Y-%m-%d %H:%M:%S')
        end_datetime = current_datetime + timedelta(minutes=duration_int)
        is_working_end, error_message_end = Schedule.is_working_time(record['trainer_id'], end_datetime)
        if not is_working_end:
            return jsonify({
                'error': 'Validation Error',
                'message': f'Тренировка заканчивается вне рабочего времени тренера: {error_message_end}'
            }), 400
        
        # Проверка на конфликт при изменении длительности
        if Record.exists_conflicting_record(record['trainer_id'], record['datetime'], duration_int, exclude_record_id=record_id):
            return jsonify({
                'error': 'Conflict',
                'message': 'Увеличение длительности создает конфликт с существующими записями'
            }), 409
    
    # Обновляем запись
    updated_record = Record.update(record_id, datetime_str=datetime_formatted, duration=duration_int, status=status)
    
    if not updated_record:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Ошибка при обновлении записи'
        }), 500
    
    # Получаем информацию о тренере для ответа
    trainer = Trainer.get_by_id(updated_record['trainer_id'])
    
    return jsonify({
        'message': 'Запись успешно обновлена',
        'record': {
            'id': updated_record['id'],
            'trainer': {
                'id': trainer['id'],
                'full_name': trainer['full_name'],
                'specialization': trainer['specialization'],
                'address': trainer.get('address'),
                'gym_name': trainer.get('gym_name')
            },
            'datetime': updated_record['datetime'],
            'duration': updated_record.get('duration', 60),
            'status': updated_record['status'],
            'created_at': updated_record['created_at']
        }
    }), 200


@bp.route('/<int:record_id>', methods=['DELETE'])
@csrf_required
@require_auth
def delete_record(record_id):
    """
    Отменить запись на тренировку (изменить статус на 'cancelled').
    
    DELETE /records/<id>
    
    Returns:
        JSON с подтверждением отмены
    """
    user_id = session.get('user_id')
    
    # Проверяем, что запись существует и принадлежит пользователю
    record = Record.get_by_id(record_id)
    
    if not record:
        return jsonify({
            'error': 'Not Found',
            'message': 'Запись не найдена'
        }), 404
    
    if not Record.belongs_to_user(record_id, user_id):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Недостаточно прав для отмены этой записи'
        }), 403
    
    # Отменяем запись (меняем статус на 'cancelled')
    cancelled_record = Record.cancel(record_id)
    
    if not cancelled_record:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Ошибка при отмене записи'
        }), 500
    
    return jsonify({
        'message': 'Запись успешно отменена',
        'record': {
            'id': cancelled_record['id'],
            'status': cancelled_record['status']
        }
    }), 200


@bp.route('/user/<int:user_id>', methods=['GET'])
@require_auth
def get_user_records(user_id):
    """
    Получить все записи конкретного пользователя.
    
    GET /records/user/<user_id>
    Query Parameters:
        - status: Фильтр по статусу (pending, confirmed, cancelled, completed) - опционально
    
    Returns:
        JSON со списком записей пользователя
    """
    current_user_id = session.get('user_id')
    
    # Проверяем, что пользователь запрашивает свои записи или имеет права администратора
    # Для простоты разрешаем только просмотр своих записей
    if current_user_id != user_id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'Вы можете просматривать только свои записи'
        }), 403
    
    # Проверяем существование пользователя
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            'error': 'Not Found',
            'message': 'Пользователь не найден'
        }), 404
    
    # Получаем параметр фильтрации по статусу
    status = request.args.get('status', '').strip()
    status = status if status else None
    
    # Получаем записи пользователя
    records = Record.get_by_user(user_id, status=status)
    
    # Форматируем ответ с информацией о тренерах
    records_list = []
    for record in records:
        # Получаем информацию о тренере
        trainer = Trainer.get_by_id(record['trainer_id'])
        
        records_list.append({
            'id': record['id'],
            'trainer': {
                'id': trainer['id'] if trainer else None,
                'full_name': trainer['full_name'] if trainer else 'Тренер не найден',
                'specialization': trainer['specialization'] if trainer else None,
                'address': trainer.get('address') if trainer else None,
                'gym_name': trainer.get('gym_name') if trainer else None
            } if trainer else None,
            'datetime': record['datetime'],
            'duration': record.get('duration', 60),
            'status': record['status'],
            'created_at': record['created_at']
        })
    
    return jsonify({
        'user': {
            'id': user['id'],
            'full_name': user['full_name'],
            'email': user['email']
        },
        'records': records_list,
        'count': len(records_list)
    }), 200


@bp.route('/trainer/<int:trainer_id>', methods=['GET'])
def get_trainer_records(trainer_id):
    """
    Получить все записи конкретного тренера.
    
    GET /records/trainer/<trainer_id>
    Query Parameters:
        - status: Фильтр по статусу (pending, confirmed, cancelled, completed) - опционально
    
    Returns:
        JSON со списком записей тренера
    """
    # Проверяем существование тренера
    trainer = Trainer.get_by_id(trainer_id)
    if not trainer:
        return jsonify({
            'error': 'Not Found',
            'message': 'Тренер не найден'
        }), 404
    
    # Получаем параметр фильтрации по статусу
    status = request.args.get('status', '').strip()
    status = status if status else None
    
    # Получаем записи тренера
    records = Record.get_by_trainer(trainer_id, status=status)
    
    # Форматируем ответ с информацией о пользователях
    records_list = []
    for record in records:
        # Получаем информацию о пользователе
        user = User.get_by_id(record['user_id'])
        
        records_list.append({
            'id': record['id'],
            'user': {
                'id': user['id'] if user else None,
                'full_name': user['full_name'] if user else 'Пользователь не найден',
                'email': user.get('email') if user else None
            } if user else None,
            'datetime': record['datetime'],
            'duration': record.get('duration', 60),
            'status': record['status'],
            'created_at': record['created_at']
        })
    
    return jsonify({
        'trainer': {
            'id': trainer['id'],
            'full_name': trainer['full_name'],
            'specialization': trainer['specialization']
        },
        'records': records_list,
        'count': len(records_list)
    }), 200

