"""Модуль для работы с файловым хранилищем данных"""

import json
import os
from datetime import datetime
from typing import List, Dict
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
        Добавление пользователя в избранное в соответствии со схемой DATA_SCHEMA.md

        Ожидаемая структура user_data:
        {
            'vk_id': int,
            'first_name': str,
            'last_name': str,
            'city': str,
            'profile_url': str,
            'photo_url': str,
            'photos': list,
            'photos_attachments': list,
            'photos_likes': list
        }
        """
        favorites = self.load_favorites()

        # Проверяем по vk_id
        for fav in favorites:
            if fav.get('vk_id') == user_data.get('vk_id'):
                return False

        # Приводим к единой структуре согласно DATA_SCHEMA.md
        favorite_entry = {
            'vk_id': user_data.get('vk_id'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'city': user_data.get('city', ''),
            'profile_url': user_data.get('profile_url', ''),
            'photo_url': user_data.get('photo_url', ''),
            'photos': user_data.get('photos', []),
            'photos_attachments': user_data.get('photos_attachments', []),
            'photos_likes': user_data.get('photos_likes', []),
            'saved_at': datetime.now().isoformat()  # saved_at согласно схеме
        }

        favorites.append(favorite_entry)
        self.save_favorites(favorites)
        return True

    def remove_from_favorites(self, vk_id: int) -> bool:
        """
        Удаление пользователя из избранного по vk_id

        Args:
            vk_id: ID пользователя ВКонтакте

        Returns:
            True если удален, False если не найден
        """
        favorites = self.load_favorites()
        original_count = len(favorites)

        # Фильтруем по vk_id
        favorites = [fav for fav in favorites if fav.get('vk_id') != vk_id]

        if len(favorites) < original_count:
            self.save_favorites(favorites)
            return True

        return False

    def remove_favorite_by_index(self, index: int) -> bool:
        """
        Удаление пользователя из избранного по индексу (для пользовательского интерфейса)

        Args:
            index: индекс в списке (начиная с 0)

        Returns:
            True если удален, False если индекс не корректен
        """
        favorites = self.load_favorites()

        if 0 <= index < len(favorites):
            removed = favorites.pop(index)
            self.save_favorites(favorites)
            return True

        return False

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
        """Добавление пользователя в черный список"""
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