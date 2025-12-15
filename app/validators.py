"""
Модуль для валидации входных данных
"""
import re
from datetime import datetime


def validate_email(email):
    """
    Валидация email адреса.
    
    Args:
        email: Email для проверки
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not email:
        return False, "Email обязателен для заполнения"
    
    if not isinstance(email, str):
        return False, "Email должен быть строкой"
    
    # Базовый паттерн для email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Неверный формат email адреса"
    
    if len(email) > 255:
        return False, "Email слишком длинный (максимум 255 символов)"
    
    return True, None


def validate_password(password):
    """
    Валидация пароля.
    
    Args:
        password: Пароль для проверки
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not password:
        return False, "Пароль обязателен для заполнения"
    
    if not isinstance(password, str):
        return False, "Пароль должен быть строкой"
    
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    
    if len(password) > 128:
        return False, "Пароль слишком длинный (максимум 128 символов)"
    
    return True, None


def validate_full_name(full_name):
    """
    Валидация ФИО.
    
    Args:
        full_name: ФИО для проверки
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not full_name:
        return False, "ФИО обязательно для заполнения"
    
    if not isinstance(full_name, str):
        return False, "ФИО должно быть строкой"
    
    if len(full_name.strip()) < 2:
        return False, "ФИО должно содержать минимум 2 символа"
    
    if len(full_name) > 200:
        return False, "ФИО слишком длинное (максимум 200 символов)"
    
    # Проверка на допустимые символы (буквы, пробелы, дефисы)
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', full_name):
        return False, "ФИО может содержать только буквы, пробелы и дефисы"
    
    return True, None


def validate_passport_data(passport_data):
    """
    Валидация паспортных данных.
    
    Args:
        passport_data: Паспортные данные для проверки
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not passport_data:
        return False, "Паспортные данные обязательны для заполнения"
    
    if not isinstance(passport_data, str):
        return False, "Паспортные данные должны быть строкой"
    
    if len(passport_data.strip()) < 5:
        return False, "Паспортные данные должны содержать минимум 5 символов"
    
    if len(passport_data) > 100:
        return False, "Паспортные данные слишком длинные (максимум 100 символов)"
    
    return True, None


def validate_datetime(datetime_str):
    """
    Валидация даты и времени.
    
    Args:
        datetime_str: Дата и время в формате 'YYYY-MM-DD HH:MM:SS' или 'YYYY-MM-DDTHH:MM:SS'
        
    Returns:
        tuple: (is_valid: bool, error_message: str, datetime_obj: datetime or None)
    """
    if not datetime_str:
        return False, "Дата и время обязательны", None
    
    if not isinstance(datetime_str, str):
        return False, "Дата и время должны быть строкой", None
    
    # Пробуем разные форматы
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M'
    ]
    
    datetime_obj = None
    for fmt in formats:
        try:
            datetime_obj = datetime.strptime(datetime_str, fmt)
            break
        except ValueError:
            continue
    
    if datetime_obj is None:
        return False, "Неверный формат даты и времени. Используйте: YYYY-MM-DD HH:MM:SS", None
    
    # Проверяем, что дата в будущем
    if datetime_obj <= datetime.now():
        return False, "Дата и время должны быть в будущем", None
    
    return True, None, datetime_obj


def validate_rating(rating):
    """
    Валидация оценки (1-5).
    
    Args:
        rating: Оценка для проверки
        
    Returns:
        tuple: (is_valid: bool, error_message: str, rating_int: int or None)
    """
    if rating is None:
        return False, "Оценка обязательна", None
    
    try:
        rating_int = int(rating)
    except (ValueError, TypeError):
        return False, "Оценка должна быть числом", None
    
    if rating_int < 1 or rating_int > 5:
        return False, "Оценка должна быть от 1 до 5", None
    
    return True, None, rating_int


def validate_address(address):
    """
    Валидация адреса.
    
    Args:
        address: Адрес для проверки (может быть None, так как поле опциональное)
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # Адрес опциональный, если None или пустая строка - это OK
    if address is None or (isinstance(address, str) and not address.strip()):
        return True, None
    
    if not isinstance(address, str):
        return False, "Адрес должен быть строкой"
    
    if len(address.strip()) < 5:
        return False, "Адрес должен содержать минимум 5 символов"
    
    if len(address) > 500:
        return False, "Адрес слишком длинный (максимум 500 символов)"
    
    # Проверка на допустимые символы (буквы, цифры, пробелы, дефисы, точки, запятые, скобки, номер)
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9\s\-\.,\(\)\/№]+$', address):
        return False, "Адрес содержит недопустимые символы"
    
    return True, None


def validate_gym_name(gym_name):
    """
    Валидация названия зала.
    
    Args:
        gym_name: Название зала для проверки (может быть None, так как поле опциональное)
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # Название зала опциональное, если None или пустая строка - это OK
    if gym_name is None or (isinstance(gym_name, str) and not gym_name.strip()):
        return True, None
    
    if not isinstance(gym_name, str):
        return False, "Название зала должно быть строкой"
    
    if len(gym_name.strip()) < 2:
        return False, "Название зала должно содержать минимум 2 символа"
    
    if len(gym_name) > 200:
        return False, "Название зала слишком длинное (максимум 200 символов)"
    
    # Проверка на допустимые символы (буквы, цифры, пробелы, дефисы, кавычки)
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9\s\-"«»]+$', gym_name):
        return False, "Название зала содержит недопустимые символы"
    
    return True, None


def validate_required_fields(data, required_fields):
    """
    Проверка наличия обязательных полей.
    
    Args:
        data: Словарь с данными
        required_fields: Список обязательных полей
        
    Returns:
        tuple: (is_valid: bool, missing_fields: list)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields


def validate_time(time_str):
    """
    Валидация времени в формате HH:MM.
    
    Args:
        time_str: Время для проверки (формат HH:MM)
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not time_str:
        return False, "Время обязательно для заполнения"
    
    if not isinstance(time_str, str):
        return False, "Время должно быть строкой"
    
    # Проверка формата HH:MM
    pattern = r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$'
    if not re.match(pattern, time_str):
        return False, "Неверный формат времени. Используйте формат HH:MM (например, 09:00)"
    
    return True, None


def validate_day_of_week(day_of_week):
    """
    Валидация дня недели (0-6, где 0=понедельник, 6=воскресенье).
    
    Args:
        day_of_week: День недели для проверки
        
    Returns:
        tuple: (is_valid: bool, error_message: str, day_int: int or None)
    """
    if day_of_week is None:
        return False, "День недели обязателен", None
    
    try:
        day_int = int(day_of_week)
    except (ValueError, TypeError):
        return False, "День недели должен быть числом от 0 до 6", None
    
    if day_int < 0 or day_int > 6:
        return False, "День недели должен быть от 0 (понедельник) до 6 (воскресенье)", None
    
    return True, None, day_int


def validate_duration(duration):
    """
    Валидация длительности тренировки в минутах.
    
    Args:
        duration: Длительность в минутах
        
    Returns:
        tuple: (is_valid: bool, error_message: str, duration_int: int)
    """
    if duration is None:
        return True, None, 60  # По умолчанию 60 минут
    
    try:
        duration_int = int(duration)
        if duration_int <= 0:
            return False, "Длительность должна быть положительным числом", None
        if duration_int > 480:  # Максимум 8 часов
            return False, "Длительность не может превышать 480 минут (8 часов)", None
        return True, None, duration_int
    except (ValueError, TypeError):
        return False, "Длительность должна быть числом (в минутах)", None

