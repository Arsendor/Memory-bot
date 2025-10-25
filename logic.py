from datetime import datetime, timedelta
import json
import random

class ReviewLogic:
    def __init__(self):
        # Интервалы повторения (1 день, 3 дня, 7 дней, 14 дней, 30 дней)
        self.intervals = [1, 3, 7, 14, 30]
        self.data = self.load_data()
        
    def load_data(self):
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_data(self):
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def init_user(self, user_id):
        """Инициализация данных пользователя"""
        if user_id not in self.data:
            self.data[user_id] = {
                'materials': [],
                'stats': {
                    'completed': 0,
                    'in_progress': 0,
                    'streak': 0,
                    'last_review': None,
                    'achievements': []
                }
            }
            self.save_data()

    def add_material(self, user_id, text):
        """Добавить новый материал для повторения"""
        self.init_user(user_id)
        
        # Создаем расписание повторений
        next_dates = []
        current_date = datetime.now()
        
        for days in self.intervals:
            next_date = current_date + timedelta(days=days)
            next_dates.append(next_date.strftime("%Y-%m-%d"))

        material = {
            "text": text,
            "review_dates": next_dates,
            "current_step": 0,
            "completed": False,
            "added_date": current_date.strftime("%Y-%m-%d"),
            "last_reviewed": None
        }

        self.data[user_id]['materials'].append(material)
        self.data[user_id]['stats']['in_progress'] += 1
        self.save_data()

    def get_reviews(self, user_id):
        """Получить материалы для повторения на сегодня"""
        self.init_user(user_id)
        today = datetime.now().strftime("%Y-%m-%d")
        to_review = []

        for material in self.data[user_id]['materials']:
            if not material["completed"]:
                current_step = material["current_step"]
                if current_step < len(self.intervals):
                    if material["review_dates"][current_step] <= today:
                        to_review.append(material)

        return to_review

    def mark_reviewed(self, user_id, text):
        """Отметить материал как повторенный"""
        self.init_user(user_id)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Обновляем серию повторений
        last_review = self.data[user_id]['stats']['last_review']
        if last_review:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if last_review == yesterday:
                self.data[user_id]['stats']['streak'] += 1
            elif last_review != today:
                self.data[user_id]['stats']['streak'] = 1
        else:
            self.data[user_id]['stats']['streak'] = 1
        
        self.data[user_id]['stats']['last_review'] = today

        for material in self.data[user_id]['materials']:
            if material["text"] == text and not material["completed"]:
                material["current_step"] += 1
                material["last_reviewed"] = today
                
                if material["current_step"] >= len(self.intervals):
                    material["completed"] = True
                    self.data[user_id]['stats']['completed'] += 1
                    self.data[user_id]['stats']['in_progress'] -= 1
                    
                    # Проверяем достижения
                    self.check_achievements(user_id)
                
                self.save_data()
                break

    def get_stats(self, user_id):
        """Получить статистику пользователя"""
        self.init_user(user_id)
        stats = self.data[user_id]['stats']
        
        # Определяем уровень усердия
        streak = stats['streak']
        if streak >= 30:
            level = "Гений! 🧠"
        elif streak >= 20:
            level = "Мастер! 🎯"
        elif streak >= 10:
            level = "Продвинутый! 💪"
        elif streak >= 5:
            level = "Старательный! 📚"
        else:
            level = "Начинающий! 🌱"

        return {
            'completed': stats['completed'],
            'in_progress': stats['in_progress'],
            'streak': stats['streak'],
            'level': level,
            'achievements': stats['achievements']
        }

    def get_all_materials(self, user_id):
        """Получить список всех материалов"""
        self.init_user(user_id)
        return self.data[user_id]['materials']

    def get_random_material(self, user_id):
        """Получить случайный материал"""
        self.init_user(user_id)
        materials = self.data[user_id]['materials']
        if not materials:
            return None
        return random.choice(materials)

    def check_achievements(self, user_id):
        """Проверить и обновить достижения"""
        stats = self.data[user_id]['stats']
        achievements = stats['achievements']
        
        # Достижения за количество изученных материалов
        completed = stats['completed']
        if completed >= 50 and "Мудрец 🎓" not in achievements:
            achievements.append("Мудрец 🎓")
        elif completed >= 25 and "Знаток 📚" not in achievements:
            achievements.append("Знаток 📚")
        elif completed >= 10 and "Ученик 📖" not in achievements:
            achievements.append("Ученик 📖")
        
        # Достижения за серию повторений
        streak = stats['streak']
        if streak >= 30 and "Железная воля 💪" not in achievements:
            achievements.append("Железная воля 💪")
        elif streak >= 15 and "Настойчивость 🎯" not in achievements:
            achievements.append("Настойчивость 🎯")
        elif streak >= 7 and "Целеустремленность ⭐" not in achievements:
            achievements.append("Целеустремленность ⭐")
        
        self.save_data()
