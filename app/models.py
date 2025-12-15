"""
Модели данных для работы с базой данных
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db
from app.validators import validate_address, validate_gym_name
from datetime import datetime


class User:
    """Модель пользователя"""
    
    @staticmethod
    def create(full_name, email, password, passport_data):
        """
        Создать нового пользователя.
        
        Args:
            full_name: ФИО пользователя
            email: Email (должен быть уникальным)
            password: Пароль (будет захеширован)
            passport_data: Паспортные данные
            
        Returns:
            dict: Созданный пользователь или None при ошибке
        """
        db = get_db()
        try:
            password_hash = generate_password_hash(password)
            cursor = db.execute(
                'INSERT INTO users (full_name, email, password_hash, passport_data) '
                'VALUES (?, ?, ?, ?)',
                (full_name, email, password_hash, passport_data)
            )
            db.commit()
            return User.get_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            db.rollback()
            return None
    
    @staticmethod
    def get_by_id(user_id):
        """Получить пользователя по ID"""
        db = get_db()
        row = db.execute(
            'SELECT id, full_name, email, passport_data, created_at FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_email(email):
        """Получить пользователя по email"""
        db = get_db()
        row = db.execute(
            'SELECT * FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def verify_password(user, password):
        """Проверить пароль пользователя"""
        if not user:
            return False
        return check_password_hash(user['password_hash'], password)


class Trainer:
    """Модель тренера"""
    
    @staticmethod
    def create(full_name, specialization, description=None, address=None, gym_name=None):
        """
        Создать нового тренера.
        
        Args:
            full_name: ФИО тренера
            specialization: Специализация
            description: Описание (опционально)
            address: Адрес (опционально)
            gym_name: Название зала (опционально)
            
        Returns:
            dict: Созданный тренер или None при ошибке валидации
            
        Raises:
            ValueError: При ошибке валидации данных
        """
        # Валидация адреса, если передан
        if address is not None:
            is_valid, error = validate_address(address)
            if not is_valid:
                raise ValueError(f"Ошибка валидации адреса: {error}")
        
        # Валидация названия зала, если передано
        if gym_name is not None:
            is_valid, error = validate_gym_name(gym_name)
            if not is_valid:
                raise ValueError(f"Ошибка валидации названия зала: {error}")
        
        db = get_db()
        cursor = db.execute(
            'INSERT INTO trainers (full_name, specialization, description, address, gym_name) '
            'VALUES (?, ?, ?, ?, ?)',
            (full_name, specialization, description, address, gym_name)
        )
        db.commit()
        return Trainer.get_by_id(cursor.lastrowid)
    
    @staticmethod
    def get_by_id(trainer_id):
        """Получить тренера по ID"""
        db = get_db()
        row = db.execute(
            'SELECT * FROM trainers WHERE id = ?',
            (trainer_id,)
        ).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_all(specialization=None, search=None):
        """
        Получить список всех тренеров с фильтрацией.
        
        Args:
            specialization: Фильтр по специализации
            search: Поиск по ФИО
            
        Returns:
            list: Список тренеров
        """
        db = get_db()
        query = 'SELECT * FROM trainers WHERE 1=1'
        params = []
        
        if specialization:
            query += ' AND specialization = ?'
            params.append(specialization)
        
        if search:
            query += ' AND full_name LIKE ?'
            params.append(f'%{search}%')
        
        query += ' ORDER BY full_name'
        
        rows = db.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def exists(trainer_id):
        """Проверить существование тренера"""
        return Trainer.get_by_id(trainer_id) is not None


class Record:
    """Модель записи на тренировку"""
    
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    
    @staticmethod
    def create(user_id, trainer_id, datetime_str, duration=60, status=STATUS_PENDING):
        """
        Создать новую запись на тренировку.
        
        Args:
            user_id: ID пользователя
            trainer_id: ID тренера
            datetime_str: Дата и время в формате ISO (YYYY-MM-DD HH:MM:SS)
            duration: Длительность тренировки в минутах (по умолчанию 60)
            status: Статус записи (по умолчанию 'pending')
            
        Returns:
            dict: Созданная запись или None при ошибке
        """
        db = get_db()
        try:
            cursor = db.execute(
                'INSERT INTO records (user_id, trainer_id, datetime, duration, status) '
                'VALUES (?, ?, ?, ?, ?)',
                (user_id, trainer_id, datetime_str, duration, status)
            )
            db.commit()
            return Record.get_by_id(cursor.lastrowid)
        except Exception as e:
            db.rollback()
            return None
    
    @staticmethod
    def get_by_id(record_id):
        """Получить запись по ID"""
        db = get_db()
        row = db.execute(
            'SELECT * FROM records WHERE id = ?',
            (record_id,)
        ).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_user(user_id, status=None):
        """
        Получить все записи пользователя.
        
        Args:
            user_id: ID пользователя
            status: Фильтр по статусу (опционально)
            
        Returns:
            list: Список записей
        """
        db = get_db()
        if status:
            rows = db.execute(
                'SELECT * FROM records WHERE user_id = ? AND status = ? ORDER BY datetime DESC',
                (user_id, status)
            ).fetchall()
        else:
            rows = db.execute(
                'SELECT * FROM records WHERE user_id = ? ORDER BY datetime DESC',
                (user_id,)
            ).fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_trainer(trainer_id, status=None):
        """
        Получить все записи тренера.
        
        Args:
            trainer_id: ID тренера
            status: Фильтр по статусу (опционально)
            
        Returns:
            list: Список записей
        """
        db = get_db()
        if status:
            rows = db.execute(
                'SELECT * FROM records WHERE trainer_id = ? AND status = ? ORDER BY datetime DESC',
                (trainer_id, status)
            ).fetchall()
        else:
            rows = db.execute(
                'SELECT * FROM records WHERE trainer_id = ? ORDER BY datetime DESC',
                (trainer_id,)
            ).fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(record_id, datetime_str=None, duration=None, status=None):
        """
        Обновить запись.
        
        Args:
            record_id: ID записи
            datetime_str: Новая дата/время (опционально)
            duration: Новая длительность в минутах (опционально)
            status: Новый статус (опционально)
            
        Returns:
            dict: Обновленная запись или None
        """
        db = get_db()
        updates = []
        params = []
        
        if datetime_str is not None:
            updates.append('datetime = ?')
            params.append(datetime_str)
        
        if duration is not None:
            updates.append('duration = ?')
            params.append(duration)
        
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        
        if not updates:
            return Record.get_by_id(record_id)
        
        params.append(record_id)
        try:
            db.execute(
                f'UPDATE records SET {", ".join(updates)} WHERE id = ?',
                params
            )
            db.commit()
            return Record.get_by_id(record_id)
        except Exception as e:
            db.rollback()
            return None
    
    @staticmethod
    def cancel(record_id):
        """Отменить запись (изменить статус на 'cancelled')"""
        return Record.update(record_id, status=Record.STATUS_CANCELLED)
    
    @staticmethod
    def belongs_to_user(record_id, user_id):
        """Проверить, принадлежит ли запись пользователю"""
        record = Record.get_by_id(record_id)
        return record and record['user_id'] == user_id
    
    @staticmethod
    def exists_conflicting_record(trainer_id, datetime_str, duration, exclude_record_id=None):
        """
        Проверить, существует ли запись, которая перекрывается по времени с новой записью.
        Учитываются только активные записи (не cancelled).
        Проверяет перекрытие не только по времени начала, но и на протяжении всей длительности.
        
        Args:
            trainer_id: ID тренера
            datetime_str: Дата и время начала в формате ISO (YYYY-MM-DD HH:MM:SS)
            duration: Длительность новой записи в минутах
            exclude_record_id: ID записи, которую нужно исключить из проверки (для обновления)
            
        Returns:
            bool: True если конфликтующая запись существует
        """
        from datetime import datetime, timedelta
        
        db = get_db()
        
        # Парсим время начала новой записи
        start_time = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        end_time = start_time + timedelta(minutes=duration)
        
        # Получаем все активные записи тренера
        query = '''
            SELECT id, datetime, duration FROM records 
            WHERE trainer_id = ? 
            AND status != ?
        '''
        params = [trainer_id, Record.STATUS_CANCELLED]
        
        if exclude_record_id:
            query += ' AND id != ?'
            params.append(exclude_record_id)
        
        rows = db.execute(query, params).fetchall()
        
        # Проверяем каждую запись на перекрытие
        for row in rows:
            existing_start = datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S')
            existing_duration = row['duration'] or 60  # По умолчанию 60 минут, если не указано
            existing_end = existing_start + timedelta(minutes=existing_duration)
            
            # Проверяем перекрытие: новая запись начинается до окончания существующей
            # и заканчивается после начала существующей
            if start_time < existing_end and end_time > existing_start:
                return True
        
        return False


class Review:
    """Модель отзыва"""
    
    @staticmethod
    def create(user_id, trainer_id, text, rating):
        """
        Создать новый отзыв.
        
        Args:
            user_id: ID пользователя
            trainer_id: ID тренера
            text: Текст отзыва
            rating: Оценка (1-5)
            
        Returns:
            dict: Созданный отзыв или None при ошибке
        """
        db = get_db()
        try:
            cursor = db.execute(
                'INSERT INTO reviews (user_id, trainer_id, text, rating) '
                'VALUES (?, ?, ?, ?)',
                (user_id, trainer_id, text, rating)
            )
            db.commit()
            return Review.get_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            db.rollback()
            return None
    
    @staticmethod
    def get_by_id(review_id):
        """Получить отзыв по ID"""
        db = get_db()
        row = db.execute(
            'SELECT * FROM reviews WHERE id = ?',
            (review_id,)
        ).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_trainer(trainer_id):
        """
        Получить все отзывы о тренере.
        
        Args:
            trainer_id: ID тренера
            
        Returns:
            list: Список отзывов с информацией о пользователях
        """
        db = get_db()
        rows = db.execute(
            '''SELECT r.*, u.full_name as user_name 
               FROM reviews r 
               JOIN users u ON r.user_id = u.id 
               WHERE r.trainer_id = ? 
               ORDER BY r.created_at DESC''',
            (trainer_id,)
        ).fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_user_and_trainer(user_id, trainer_id):
        """Получить отзыв пользователя о конкретном тренере"""
        db = get_db()
        row = db.execute(
            'SELECT * FROM reviews WHERE user_id = ? AND trainer_id = ?',
            (user_id, trainer_id)
        ).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def update(review_id, text=None, rating=None):
        """
        Обновить отзыв.
        
        Args:
            review_id: ID отзыва
            text: Новый текст (опционально)
            rating: Новая оценка (опционально)
            
        Returns:
            dict: Обновленный отзыв или None
        """
        db = get_db()
        updates = []
        params = []
        
        if text is not None:
            updates.append('text = ?')
            params.append(text)
        
        if rating is not None:
            updates.append('rating = ?')
            params.append(rating)
        
        if not updates:
            return Review.get_by_id(review_id)
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(review_id)
        
        db.execute(
            f'UPDATE reviews SET {", ".join(updates)} WHERE id = ?',
            params
        )
        db.commit()
        return Review.get_by_id(review_id)
    
    @staticmethod
    def belongs_to_user(review_id, user_id):
        """Проверить, принадлежит ли отзыв пользователю"""
        review = Review.get_by_id(review_id)
        return review and review['user_id'] == user_id


class Schedule:
    """Модель расписания работы тренера"""
    
    # Дни недели: 0=понедельник, 1=вторник, ..., 6=воскресенье
    DAYS_OF_WEEK = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }
    
    @staticmethod
    def create(trainer_id, day_of_week, start_time, end_time, is_active=True):
        """
        Создать запись расписания для тренера.
        
        Args:
            trainer_id: ID тренера
            day_of_week: День недели (0-6, где 0=понедельник)
            start_time: Время начала работы (формат HH:MM)
            end_time: Время окончания работы (формат HH:MM)
            is_active: Активно ли расписание (по умолчанию True)
            
        Returns:
            dict: Созданное расписание или None при ошибке
        """
        db = get_db()
        try:
            cursor = db.execute(
                'INSERT INTO schedules (trainer_id, day_of_week, start_time, end_time, is_active) '
                'VALUES (?, ?, ?, ?, ?)',
                (trainer_id, day_of_week, start_time, end_time, 1 if is_active else 0)
            )
            db.commit()
            return Schedule.get_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            db.rollback()
            return None
    
    @staticmethod
    def get_by_id(schedule_id):
        """Получить расписание по ID"""
        db = get_db()
        row = db.execute(
            'SELECT * FROM schedules WHERE id = ?',
            (schedule_id,)
        ).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_trainer(trainer_id):
        """
        Получить все расписания тренера.
        
        Args:
            trainer_id: ID тренера
            
        Returns:
            list: Список расписаний, отсортированный по дню недели
        """
        db = get_db()
        rows = db.execute(
            'SELECT * FROM schedules WHERE trainer_id = ? ORDER BY day_of_week, start_time',
            (trainer_id,)
        ).fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_trainer_and_day(trainer_id, day_of_week):
        """Получить расписание тренера на конкретный день недели"""
        db = get_db()
        row = db.execute(
            'SELECT * FROM schedules WHERE trainer_id = ? AND day_of_week = ?',
            (trainer_id, day_of_week)
        ).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def update(schedule_id, start_time=None, end_time=None, is_active=None):
        """
        Обновить расписание.
        
        Args:
            schedule_id: ID расписания
            start_time: Новое время начала (опционально)
            end_time: Новое время окончания (опционально)
            is_active: Новый статус активности (опционально)
            
        Returns:
            dict: Обновленное расписание или None
        """
        db = get_db()
        updates = []
        params = []
        
        if start_time is not None:
            updates.append('start_time = ?')
            params.append(start_time)
        
        if end_time is not None:
            updates.append('end_time = ?')
            params.append(end_time)
        
        if is_active is not None:
            updates.append('is_active = ?')
            params.append(1 if is_active else 0)
        
        if not updates:
            return Schedule.get_by_id(schedule_id)
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(schedule_id)
        
        db.execute(
            f'UPDATE schedules SET {", ".join(updates)} WHERE id = ?',
            params
        )
        db.commit()
        return Schedule.get_by_id(schedule_id)
    
    @staticmethod
    def delete(schedule_id):
        """
        Удалить расписание.
        
        Args:
            schedule_id: ID расписания
            
        Returns:
            bool: True если удалено, False если не найдено
        """
        db = get_db()
        cursor = db.execute('DELETE FROM schedules WHERE id = ?', (schedule_id,))
        db.commit()
        return cursor.rowcount > 0
    
    @staticmethod
    def exists(schedule_id):
        """Проверить существование расписания"""
        return Schedule.get_by_id(schedule_id) is not None
    
    @staticmethod
    def is_working_time(trainer_id, datetime_obj):
        """
        Проверить, работает ли тренер в указанное время.
        
        Args:
            trainer_id: ID тренера
            datetime_obj: Объект datetime для проверки
            
        Returns:
            tuple: (is_working: bool, error_message: str or None)
        """
        from datetime import datetime
        
        # Определяем день недели (0=понедельник, 6=воскресенье)
        # datetime.weekday() возвращает 0=понедельник, 6=воскресенье
        day_of_week = datetime_obj.weekday()
        
        # Получаем расписание на этот день недели
        schedule = Schedule.get_by_trainer_and_day(trainer_id, day_of_week)
        
        if not schedule:
            day_name = Schedule.DAYS_OF_WEEK.get(day_of_week, 'этот день')
            return False, f'Тренер не работает в {day_name.lower()}'
        
        # Проверяем, активно ли расписание
        if not schedule['is_active']:
            day_name = Schedule.DAYS_OF_WEEK.get(day_of_week, 'этот день')
            return False, f'Расписание на {day_name.lower()} временно неактивно'
        
        # Получаем время записи
        record_time = datetime_obj.strftime('%H:%M')
        
        # Получаем рабочее время тренера
        start_time = schedule['start_time']
        end_time = schedule['end_time']
        
        # Сравниваем время
        record_hours, record_minutes = map(int, record_time.split(':'))
        start_hours, start_minutes = map(int, start_time.split(':'))
        end_hours, end_minutes = map(int, end_time.split(':'))
        
        record_total = record_hours * 60 + record_minutes
        start_total = start_hours * 60 + start_minutes
        end_total = end_hours * 60 + end_minutes
        
        if record_total < start_total or record_total >= end_total:
            day_name = Schedule.DAYS_OF_WEEK.get(day_of_week, 'этот день')
            return False, f'Время записи не попадает в рабочее время тренера в {day_name.lower()} ({start_time} - {end_time})'
        
        return True, None

