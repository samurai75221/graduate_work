import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from functools import wraps


def ensure_file_exists(filename: str):
    """Декоратор для проверки существования файла"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not os.path.exists(filename):
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class Storage:
    """Класс для работы с JSON хранилищем"""

    def __init__(self, favorites_file='favorites.json', blacklist_file='blacklist.json'):
        """Инициализация хранилища"""
        self.favorites_file = favorites_file
        self.blacklist_file = blacklist_file

    @ensure_file_exists('favorites.json')
    def load_favorites(self) -> List[Dict]:
        """Загрузка списка избранных"""
        with open(self.favorites_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_favorites(self, data: List[Dict]):
        """Сохранение списка избранных"""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_to_favorites(self, user_data: Dict) -> bool:
        """
        Добавление пользователя в избранное

        Args:
            user_data: данные пользователя

        Returns:
            True если добавлен, False если уже существует
        """
        favorites = self.load_favorites()

        # Проверяем, не в избранном ли уже
        for fav in favorites:
            if fav['id'] == user_data['id']:
                return False

        # Добавляем временную метку
        user_data['added_at'] = datetime.now().isoformat()
        favorites.append(user_data)
        self.save_favorites(favorites)
        return True

    def remove_from_favorites(self, user_id: int) -> bool:
        """
        Удаление пользователя из избранного

        Args:
            user_id: ID пользователя

        Returns:
            True если удален, False если не найден
        """
        favorites = self.load_favorites()
        favorites = [fav for fav in favorites if fav['id'] != user_id]
        self.save_favorites(favorites)
        return True

    def get_favorites(self) -> List[Dict]:
        """Получение списка избранных"""
        return self.load_favorites()

    @ensure_file_exists('blacklist.json')
    def load_blacklist(self) -> List[int]:
        """Загрузка черного списка"""
        with open(self.blacklist_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_blacklist(self, data: List[int]):
        """Сохранение черного списка"""
        with open(self.blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_to_blacklist(self, user_id: int) -> bool:
        """
        Добавление пользователя в черный список

        Args:
            user_id: ID пользователя

        Returns:
            True если добавлен, False если уже в списке
        """
        blacklist = self.load_blacklist()
        if user_id in blacklist:
            return False

        blacklist.append(user_id)
        self.save_blacklist(blacklist)
        return True

    def is_blacklisted(self, user_id: int) -> bool:
        """Проверка, находится ли пользователь в черном списке"""
        blacklist = self.load_blacklist()
        return user_id in blacklist