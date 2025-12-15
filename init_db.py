"""
Скрипт для инициализации базы данных
Запуск: python init_db.py
"""
from app import create_app
from app.database import init_db

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("Инициализация базы данных...")
        init_db()
        print("База данных успешно инициализирована!")
        print(f"База данных находится в: {app.config['DATABASE_PATH']}")

