"""
Скрипт для добавления тестовых тренеров в базу данных
Запуск: python add_test_trainers.py
"""
from app import create_app
from app.models import Trainer, Schedule

def add_schedule_for_trainer(trainer_id, schedules_config):
    """
    Добавить расписание для тренера.
    
    Args:
        trainer_id: ID тренера
        schedules_config: Список словарей с расписанием
            [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '18:00'}, ...]
    """
    created_count = 0
    for schedule_config in schedules_config:
        try:
            schedule = Schedule.create(
                trainer_id=trainer_id,
                day_of_week=schedule_config['day_of_week'],
                start_time=schedule_config['start_time'],
                end_time=schedule_config['end_time'],
                is_active=schedule_config.get('is_active', True)
            )
            if schedule:
                created_count += 1
        except Exception as e:
            print(f"    ⚠ Ошибка при создании расписания на день {schedule_config['day_of_week']}: {e}")
    return created_count

def add_test_trainers():
    """Добавить тестовых тренеров с расписанием"""
    app = create_app()
    
    with app.app_context():
        trainers_data = [
            {
                'full_name': 'Иванов Иван Иванович',
                'specialization': 'Фитнес',
                'description': 'Опытный фитнес-тренер с 10-летним стажем. Специализация: силовые тренировки, кардио, похудение.',
                'address': 'г. Москва, ул. Ленина, д. 10',
                'gym_name': 'Фитнес-клуб "Сила"',
                'schedule': [
                    {'day_of_week': 0, 'start_time': '09:00', 'end_time': '18:00'},  # Понедельник
                    {'day_of_week': 1, 'start_time': '09:00', 'end_time': '18:00'},  # Вторник
                    {'day_of_week': 2, 'start_time': '09:00', 'end_time': '18:00'},  # Среда
                    {'day_of_week': 3, 'start_time': '09:00', 'end_time': '18:00'},  # Четверг
                    {'day_of_week': 4, 'start_time': '09:00', 'end_time': '18:00'},  # Пятница
                ]
            },
            {
                'full_name': 'Петрова Мария Сергеевна',
                'specialization': 'Йога',
                'description': 'Сертифицированный инструктор по йоге. Провожу индивидуальные и групповые занятия.',
                'address': 'г. Москва, пр. Мира, д. 25, офис 301',
                'gym_name': 'Студия йоги "Гармония"',
                'schedule': [
                    {'day_of_week': 0, 'start_time': '10:00', 'end_time': '20:00'},  # Понедельник
                    {'day_of_week': 1, 'start_time': '10:00', 'end_time': '20:00'},  # Вторник
                    {'day_of_week': 2, 'start_time': '10:00', 'end_time': '20:00'},  # Среда
                    {'day_of_week': 3, 'start_time': '10:00', 'end_time': '20:00'},  # Четверг
                    {'day_of_week': 4, 'start_time': '10:00', 'end_time': '20:00'},  # Пятница
                    {'day_of_week': 5, 'start_time': '09:00', 'end_time': '15:00'},  # Суббота
                ]
            },
            {
                'full_name': 'Сидоров Петр Александрович',
                'specialization': 'Бокс',
                'description': 'Мастер спорта по боксу. Тренирую как начинающих, так и профессиональных спортсменов.',
                'address': 'г. Москва, ул. Спортивная, д. 5',
                'gym_name': 'Боксерский клуб "Чемпион"',
                'schedule': [
                    {'day_of_week': 0, 'start_time': '14:00', 'end_time': '22:00'},  # Понедельник
                    {'day_of_week': 1, 'start_time': '14:00', 'end_time': '22:00'},  # Вторник
                    {'day_of_week': 2, 'start_time': '14:00', 'end_time': '22:00'},  # Среда
                    {'day_of_week': 3, 'start_time': '14:00', 'end_time': '22:00'},  # Четверг
                    {'day_of_week': 4, 'start_time': '14:00', 'end_time': '22:00'},  # Пятница
                    {'day_of_week': 5, 'start_time': '10:00', 'end_time': '18:00'},  # Суббота
                ]
            },
            {
                'full_name': 'Козлова Анна Дмитриевна',
                'specialization': 'Плавание',
                'description': 'Тренер по плаванию для детей и взрослых. Опыт работы 15 лет.',
                'address': 'г. Москва, ул. Водная, д. 12',
                'gym_name': 'Бассейн "Волна"',
                'schedule': [
                    {'day_of_week': 0, 'start_time': '08:00', 'end_time': '16:00'},  # Понедельник
                    {'day_of_week': 1, 'start_time': '08:00', 'end_time': '16:00'},  # Вторник
                    {'day_of_week': 2, 'start_time': '08:00', 'end_time': '16:00'},  # Среда
                    {'day_of_week': 3, 'start_time': '08:00', 'end_time': '16:00'},  # Четверг
                    {'day_of_week': 4, 'start_time': '08:00', 'end_time': '16:00'},  # Пятница
                ]
            },
            {
                'full_name': 'Иванов Алексей Викторович',
                'specialization': 'Фитнес',
                'description': 'Персональный тренер по фитнесу. Программы для набора мышечной массы.',
                'address': 'г. Москва, ул. Силовая, д. 8',
                'gym_name': 'Тренажерный зал "Максимум"',
                'schedule': [
                    {'day_of_week': 0, 'start_time': '07:00', 'end_time': '15:00'},  # Понедельник
                    {'day_of_week': 1, 'start_time': '07:00', 'end_time': '15:00'},  # Вторник
                    {'day_of_week': 2, 'start_time': '07:00', 'end_time': '15:00'},  # Среда
                    {'day_of_week': 3, 'start_time': '07:00', 'end_time': '15:00'},  # Четверг
                    {'day_of_week': 4, 'start_time': '07:00', 'end_time': '15:00'},  # Пятница
                    {'day_of_week': 5, 'start_time': '09:00', 'end_time': '13:00'},  # Суббота
                ]
            },
            {
                'full_name': 'Смирнов Дмитрий Олегович',
                'specialization': 'Бег',
                'description': 'Тренер по бегу. Подготовка к марафонам и улучшение выносливости.',
                'address': 'г. Москва, Парк Победы, беговая дорожка №3',
                'gym_name': 'Беговой клуб "Спринт"',
                'schedule': [
                    {'day_of_week': 0, 'start_time': '06:00', 'end_time': '10:00'},  # Понедельник (утренние пробежки)
                    {'day_of_week': 1, 'start_time': '06:00', 'end_time': '10:00'},  # Вторник
                    {'day_of_week': 2, 'start_time': '06:00', 'end_time': '10:00'},  # Среда
                    {'day_of_week': 3, 'start_time': '06:00', 'end_time': '10:00'},  # Четверг
                    {'day_of_week': 4, 'start_time': '06:00', 'end_time': '10:00'},  # Пятница
                    {'day_of_week': 5, 'start_time': '07:00', 'end_time': '12:00'},  # Суббота
                    {'day_of_week': 6, 'start_time': '08:00', 'end_time': '11:00'},  # Воскресенье
                ]
            }
        ]
        
        print("Добавление тестовых тренеров и их расписания...")
        total_trainers = 0
        total_schedules = 0
        
        for trainer_data in trainers_data:
            try:
                # Создаем тренера
                trainer = Trainer.create(
                    full_name=trainer_data['full_name'],
                    specialization=trainer_data['specialization'],
                    description=trainer_data['description'],
                    address=trainer_data.get('address'),
                    gym_name=trainer_data.get('gym_name')
                )
                
                if trainer:
                    print(f"✓ Добавлен тренер: {trainer['full_name']} ({trainer['specialization']})")
                    total_trainers += 1
                    
                    # Добавляем расписание для тренера
                    schedule_list = trainer_data.get('schedule', [])
                    if schedule_list:
                        created = add_schedule_for_trainer(trainer['id'], schedule_list)
                        total_schedules += created
                        if created > 0:
                            print(f"  ✓ Добавлено расписаний: {created}")
                else:
                    print(f"✗ Ошибка при добавлении: {trainer_data['full_name']}")
                    
            except ValueError as e:
                print(f"✗ Ошибка валидации для {trainer_data['full_name']}: {e}")
            except Exception as e:
                print(f"✗ Неожиданная ошибка при добавлении {trainer_data['full_name']}: {e}")
        
        print(f"\n✓ Готово! Добавлено тренеров: {total_trainers}, расписаний: {total_schedules}")

if __name__ == '__main__':
    add_test_trainers()

