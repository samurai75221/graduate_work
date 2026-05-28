"""Модуль для работы с API ВКонтакте"""

import random
import time
from typing import List, Dict, Optional, Tuple
import vk_api
from vk_api.exceptions import ApiError
from config import VK_GROUP_TOKEN, VK_API_VERSION, SEARCH_COUNT, PHOTOS_COUNT


class VKClient:
    """Клиент для взаимодействия с API ВКонтакте"""

    def __init__(self, token: str):
        """Инициализация клиента"""
        self.token = token
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.user_id = None

    def get_user_info(self, user_id: int) -> Dict:
        """
        Получение информации о пользователе

        Args:
            user_id: ID пользователя ВК

        Returns:
            Dict с данными пользователя
        """
        try:
            response = self.vk.users.get(
                user_ids=user_id,
                fields='city,sex,bdate,country'
            )
            if response:
                user = response[0]
                return {
                    'id': user['id'],
                    'first_name': user.get('first_name', ''),
                    'last_name': user.get('last_name', ''),
                    'city': user.get('city', {}).get('title', ''),
                    'sex': user.get('sex', 0),
                    'bdate': user.get('bdate', '')
                }
        except ApiError as e:
            print(f"Ошибка получения информации о пользователе {user_id}: {e}")
        return {}

    def calculate_age(self, bdate: str) -> Optional[int]:
        """
        Вычисление возраста из даты рождения

        Args:
            bdate: дата рождения в формате DD.MM.YYYY или D.M

        Returns:
            Возраст или None
        """
        if not bdate:
            return None

        parts = bdate.split('.')
        if len(parts) == 3:  # Полная дата
            current_year = time.localtime().tm_year
            birth_year = int(parts[2])
            return current_year - birth_year
        return None

    def search_users(self, city: str, age_from: int, age_to: int, sex: int) -> List[Dict]:
        """
        Поиск пользователей по критериям

        Args:
            city: город
            age_from: минимальный возраст
            age_to: максимальный возраст
            sex: пол (1 - женский, 2 - мужской)

        Returns:
            Список найденных пользователей
        """
        try:
            # Определяем пол для поиска (противоположный)
            search_sex = 1 if sex == 2 else 2

            # Получаем ID города
            city_id = self._get_city_id(city)

            response = self.vk.users.search(
                q='',
                city=city_id,
                age_from=age_from,
                age_to=age_to,
                sex=search_sex,
                has_photo=1,
                count=SEARCH_COUNT,
                fields='id,first_name,last_name,city,photo_max,photo_id'
            )

            users = []
            for user in response.get('items', []):
                # Исключаем забаненных и удаленные страницы
                if not user.get('is_closed', True) or user.get('can_access_closed', False):
                    users.append({
                        'id': user['id'],
                        'first_name': user['first_name'],
                        'last_name': user['last_name'],
                        'city': user.get('city', {}).get('title', ''),
                        'photo_url': user.get('photo_max', ''),
                        'profile_url': f"https://vk.com/id{user['id']}"
                    })

            # Перемешиваем для разнообразия
            random.shuffle(users)
            return users

        except ApiError as e:
            print(f"Ошибка поиска пользователей: {e}")
            return []

    def _get_city_id(self, city_name: str) -> Optional[int]:
        """
        Получение ID города по названию

        Args:
            city_name: название города

        Returns:
            ID города или None
        """
        try:
            response = self.vk.database.getCities(
                q=city_name,
                need_all=0,
                count=1
            )
            if response.get('items'):
                return response['items'][0]['id']
        except ApiError:
            pass
        return 1  # По умолчанию Москва

    def get_user_photos(self, user_id: int) -> List[Tuple[str, int, str]]:
        """
        Получение топ фотографий пользователя по лайкам

        Args:
            user_id: ID пользователя

        Returns:
            Список кортежей (URL_фото, количество_лайков, attachment_строка)
        """
        try:
            response = self.vk.photos.get(
                owner_id=user_id,
                album_id='profile',
                extended=1,
                count=20,
                photo_sizes=1
            )

            photos = []
            for photo in response.get('items', []):
                likes_count = photo.get('likes', {}).get('count', 0)
                # Берем максимальный размер фото
                max_size = max(photo.get('sizes', []),
                               key=lambda x: x.get('width', 0) * x.get('height', 0))
                photo_url = max_size.get('url', '')
                # Формируем attachment для ВКонтакте
                attachment = f"photo{photo['owner_id']}_{photo['id']}"
                photos.append((photo_url, likes_count, attachment))

            # Сортируем по лайкам и берем топ PHOTOS_COUNT
            photos.sort(key=lambda x: x[1], reverse=True)
            return photos[:PHOTOS_COUNT]

        except ApiError as e:
            print(f"Ошибка получения фото пользователя {user_id}: {e}")
            return []

    def send_message(self, user_id: int, message: str, attachments: List[str] = None):
        """
        Отправка сообщения пользователю

        Args:
            user_id: ID получателя
            message: текст сообщения
            attachments: список вложений
        """
        try:
            self.vk.messages.send(
                user_id=user_id,
                message=message,
                attachment=','.join(attachments) if attachments else '',
                random_id=random.randint(1, 2 ** 31)
            )
        except ApiError as e:
            print(f"Ошибка отправки сообщения: {e}")