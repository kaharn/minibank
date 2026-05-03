import json
import os

# Путь к файлу с пользователями (папка data должна существовать)
USER_DATA_FILE = 'data/users.json'


def load_users():
    """Загружает всех пользователей из JSON файла"""
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_user(user_obj):
    """Сохраняет одного пользователя в файл"""
    users = load_users()
    # Сохраняем по ключу username
    users[user_obj.username] = user_obj.to_dict()

    # Создаем папку data, если её нет
    if not os.path.exists('data'):
        os.makedirs('data')

    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def get_user_by_username(username):
    """Ищет пользователя по его имени (для логина)"""
    users = load_users()
    return users.get(username)