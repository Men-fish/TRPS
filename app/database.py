"""
Модуль для работы с базой данных SQLite
"""
import sqlite3
from flask import g, current_app


def get_db():
    """
    Получить соединение с базой данных.
    Использует Flask g для хранения соединения в контексте запроса.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE_PATH'])
        g.db.row_factory = sqlite3.Row  # Возвращает результаты как словари
    return g.db


def close_db(e=None):
    """
    Закрыть соединение с базой данных.
    Вызывается автоматически после завершения запроса.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """
    Инициализировать базу данных - создать все таблицы.
    """
    db = get_db()
    
    # Таблица пользователей
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            passport_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица тренеров
    db.execute('''
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            description TEXT,
            address TEXT,
            gym_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Миграция: добавление новых полей для существующих таблиц
    try:
        db.execute('ALTER TABLE trainers ADD COLUMN address TEXT')
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    try:
        db.execute('ALTER TABLE trainers ADD COLUMN gym_name TEXT')
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    # Таблица записей на тренировки
    db.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trainer_id INTEGER NOT NULL,
            datetime TEXT NOT NULL,
            duration INTEGER NOT NULL DEFAULT 60,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE CASCADE,
            CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
            CHECK (duration > 0 AND duration <= 480)
        )
    ''')
    
    # Миграция: добавление поля duration для существующих таблиц
    try:
        db.execute('ALTER TABLE records ADD COLUMN duration INTEGER DEFAULT 60')
        # Обновляем существующие записи, устанавливая длительность по умолчанию
        db.execute('UPDATE records SET duration = 60 WHERE duration IS NULL')
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    # Таблица отзывов
    db.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trainer_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            rating INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE CASCADE,
            CHECK (rating >= 1 AND rating <= 5),
            UNIQUE(user_id, trainer_id)
        )
    ''')
    
    # Таблица расписания работы тренеров
    db.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainer_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE CASCADE,
            CHECK (day_of_week >= 0 AND day_of_week <= 6),
            CHECK (is_active IN (0, 1)),
            UNIQUE(trainer_id, day_of_week)
        )
    ''')
    
    # Индексы для оптимизации запросов
    db.execute('CREATE INDEX IF NOT EXISTS idx_records_user ON records(user_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_records_trainer ON records(trainer_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_reviews_trainer ON reviews(trainer_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_trainers_specialization ON trainers(specialization)')
    # Индекс для быстрой проверки конфликтов записей (тренер + время)
    db.execute('CREATE INDEX IF NOT EXISTS idx_records_trainer_datetime ON records(trainer_id, datetime)')
    # Индекс для расписания
    db.execute('CREATE INDEX IF NOT EXISTS idx_schedules_trainer ON schedules(trainer_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_schedules_trainer_day ON schedules(trainer_id, day_of_week)')
    
    db.commit()


def init_app(app):
    """
    Инициализировать приложение - зарегистрировать функции для работы с БД.
    """
    app.teardown_appcontext(close_db)

