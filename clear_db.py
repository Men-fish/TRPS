"""
Скрипт для очистки всех таблиц базы данных
Запуск: python clear_db.py
"""
from app import create_app
from app.database import get_db

def clear_all_tables():
    """Очистить все таблицы в базе данных"""
    app = create_app()
    
    with app.app_context():
        db = get_db()
        
        try:
            # Отключаем проверку внешних ключей для упрощения удаления
            db.execute('PRAGMA foreign_keys = OFF')
            
            # Удаляем данные из всех таблиц в правильном порядке
            # (сначала дочерние таблицы, потом родительские)
            tables = [
                'records',      # Зависит от users и trainers
                'reviews',      # Зависит от users и trainers
                'schedules',    # Зависит от trainers
                'users',        # Родительская таблица
                'trainers'      # Родительская таблица
            ]
            
            print("Очистка базы данных...")
            for table in tables:
                cursor = db.execute(f'DELETE FROM {table}')
                count = cursor.rowcount
                print(f"✓ Очищена таблица '{table}': удалено {count} записей")
            
            # Включаем обратно проверку внешних ключей
            db.execute('PRAGMA foreign_keys = ON')
            
            db.commit()
            print("\n✓ База данных успешно очищена!")
            
        except Exception as e:
            db.rollback()
            print(f"\n✗ Ошибка при очистке базы данных: {e}")
            raise

if __name__ == '__main__':
    clear_all_tables()

