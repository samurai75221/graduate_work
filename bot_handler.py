"""Модуль с логикой обработки сообщений бота"""

import random
from typing import Dict, List, Optional
from vk_client import VKClient
from storage import Storage


class DatingBot:
    """Бот для знакомств"""

    def __init__(self, vk_client: VKClient, storage: Storage):
        """Инициализация бота"""
        self.vk = vk_client
        self.storage = storage
        self.user_search_results = {}  # Кэш результатов поиска для каждого пользователя
        self.user_current_index = {}  # Текущий индекс просматриваемого пользователя
        self.user_current_photos = {}  # Кэш фотографий для текущего пользователя

    def handle_message(self, user_id: int, message: str) -> Optional[str]:
        """
        Обработка входящего сообщения

        Args:
            user_id: ID пользователя
            message: текст сообщения

        Returns:
            Текст ответа или None
        """
        message_lower = message.lower().strip()

        # Команды бота
        if message_lower in ['начать', 'start', 'привет']:
            return self._start_search(user_id)
        elif message_lower in ['дальше', 'next', 'следующий']:
            return self._get_next_user(user_id)
        elif message_lower in ['избранные', 'favorites', 'список']:
            return self._show_favorites(user_id)
        elif message_lower in ['добавить', 'save', 'в избранное']:
            return self._add_current_to_favorites(user_id)
        elif message_lower in ['удалить', 'remove']:
            return self._remove_from_favorites(user_id)
        elif message_lower in ['помощь', 'help', '?']:
            return self._show_help()
        elif message_lower in ['стоп', 'stop', 'exit']:
            return "До свидания! Чтобы начать поиск снова, напишите 'начать'."

        return None

    def _start_search(self, user_id: int) -> str:
        """Начало поиска пользователей"""
        # Получаем информацию о пользователе
        user_info = self.vk.get_user_info(user_id)
        if not user_info:
            return "Не удалось получить информацию о вас. Пожалуйста, проверьте настройки приватности."

        # Определяем возраст
        age = self.vk.calculate_age(user_info.get('bdate', ''))
        if not age:
            # Если возраст не определен, используем диапазон 20-30 лет
            age_from, age_to = 20, 30
        else:
            age_from, age_to = age - 5, age + 5

        # Поиск пользователей
        city = user_info.get('city', '')
        if not city:
            city = "Москва"  # Город по умолчанию

        users = self.vk.search_users(city, age_from, age_to, user_info['sex'])

        # Фильтруем черный список
        users = [u for u in users if not self.storage.is_blacklisted(u['id'])]

        if not users:
            return "К сожалению, не удалось найти пользователей по вашим критериям. Попробуйте позже."

        # Сохраняем результаты поиска
        self.user_search_results[user_id] = users
        self.user_current_index[user_id] = 0

        # Отправляем первого пользователя с фото
        return self._send_user_with_photos(user_id, users[0])

    def _send_user_with_photos(self, user_id: int, user: Dict) -> str:
        """
        Отправка пользователя с его фотографиями

        Args:
            user_id: ID пользователя, которому отправляем
            user: данные пользователя для показа

        Returns:
            Текст ответа
        """
        # Получаем фотографии пользователя
        photos = self.vk.get_user_photos(user['id'])

        # Сохраняем фотографии в кэш
        self.user_current_photos[user_id] = photos

        # Формируем текст сообщения
        message = f"🎯 Найден пользователь:\n\n"
        message += f"👤 {user['first_name']} {user['last_name']}\n"
        message += f"🏙️ Город: {user.get('city', 'Не указан')}\n"
        message += f"🔗 Ссылка: {user['profile_url']}\n\n"

        if photos:
            message += f"📸 Топ {len(photos)} фотографий (по лайкам):\n"
            for i, (_, likes, _) in enumerate(photos, 1):
                message += f"{i}. ❤️ {likes} лайков\n"
        else:
            message += "📸 Фотографии не найдены или профиль закрыт\n"

        message += "\n💡 Доступные команды:\n"
        message += "▪️ 'дальше' - следующий пользователь\n"
        message += "▪️ 'добавить' - в избранное\n"
        message += "▪️ 'избранные' - показать список\n"
        message += "▪️ 'помощь' - все команды"

        # Формируем attachments для отправки
        attachments = [photo[2] for photo in photos] if photos else []

        # Отправляем сообщение с фото
        self.vk.send_message(user_id, message, attachments)

        return None  # Сообщение уже отправлено

    def _get_next_user(self, user_id: int) -> Optional[str]:
        """Получение следующего пользователя"""
        if user_id not in self.user_search_results:
            return "Сначала начните поиск командой 'начать'."

        users = self.user_search_results[user_id]
        current_index = self.user_current_index.get(user_id, 0)

        if current_index + 1 >= len(users):
            # Поиск новых пользователей
            return self._start_search(user_id)

        self.user_current_index[user_id] = current_index + 1
        next_user = users[current_index + 1]

        # Отправляем следующего пользователя с фото
        return self._send_user_with_photos(user_id, next_user)

    def _add_current_to_favorites(self, user_id: int) -> str:
        """Добавление текущего пользователя в избранное"""
        current_user = self._get_current_user(user_id)
        if not current_user:
            return "Нет текущего пользователя для добавления. Начните поиск командой 'начать'."

        # Получаем фотографии пользователя (если еще нет в кэше)
        photos = self.user_current_photos.get(user_id)
        if not photos:
            photos = self.vk.get_user_photos(current_user['id'])

        # Добавляем фотографии к данным пользователя
        current_user['photos'] = [photo[0] for photo in photos]  # URLs
        current_user['photos_attachments'] = [photo[2] for photo in photos]  # Attachments
        current_user['photos_likes'] = [photo[1] for photo in photos]  # Likes count

        if self.storage.add_to_favorites(current_user):
            return f"✅ {current_user['first_name']} {current_user['last_name']} добавлен(а) в избранное!\n\n📸 Сохранено {len(photos)} фотографий."
        else:
            return f"⚠️ {current_user['first_name']} {current_user['last_name']} уже в избранном."

    def _remove_from_favorites(self, user_id: int) -> str:
        """Удаление пользователя из избранного"""
        favorites = self.storage.get_favorites()
        if not favorites:
            return "Ваш список избранных пуст."

        # Показываем список избранных с индексами
        response = "📋 Ваши избранные:\n\n"
        for i, fav in enumerate(favorites, 1):
            response += f"{i}. {fav['first_name']} {fav['last_name']} (ID: {fav['id']})\n"

        response += "\n✏️ Чтобы удалить, отправьте номер пользователя (например, 'удалить 1')"
        response += "\n💡 Или отправьте 'удалить все' для очистки всего списка"

        # Здесь нужно реализовать двухшаговую команду
        # Для упрощения, удаляем первого в списке
        removed_user = favorites[0]
        self.storage.remove_from_favorites(removed_user['id'])
        return f"✅ Удален(а) {removed_user['first_name']} {removed_user['last_name']} из избранного."

    def _show_favorites(self, user_id: int) -> str:
        """Показ списка избранных"""
        favorites = self.storage.get_favorites()

        if not favorites:
            return "💔 Ваш список избранных пока пуст.\n\nНачните поиск командой 'начать' и добавляйте понравившихся!"

        response = "💖 ВАШ СПИСОК ИЗБРАННЫХ 💖\n\n"
        for i, fav in enumerate(favorites, 1):
            response += f"{i}. {fav['first_name']} {fav['last_name']}\n"
            response += f"   🔗 Ссылка: {fav['profile_url']}\n"
            response += f"   📅 Добавлен: {fav.get('added_at', 'Неизвестно')[:19]}\n"

            # Показываем информацию о сохраненных фото
            if 'photos_likes' in fav and fav['photos_likes']:
                response += f"   📸 Сохранено фото: {len(fav['photos_likes'])}\n"
                response += f"   ❤️ Всего лайков: {sum(fav['photos_likes'])}\n"

            response += "\n"

        response += "💡 Команды:\n"
        response += "• 'удалить' - удалить пользователя из избранного\n"
        response += "• 'дальше' - продолжить поиск"

        return response

    def _get_current_user(self, user_id: int) -> Optional[Dict]:
        """Получение текущего просматриваемого пользователя"""
        if user_id not in self.user_search_results:
            return None

        users = self.user_search_results[user_id]
        current_index = self.user_current_index.get(user_id, 0)

        if current_index < len(users):
            return users[current_index]
        return None

    def _show_help(self) -> str:
        """Показ справки"""
        help_text = """
🤖 **БОТ ДЛЯ ЗНАКОМСТВ ВКОНТАКТЕ** 🤖

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📌 Доступные команды:**

🔹 `начать` - начать поиск пользователей
🔹 `дальше` - показать следующего пользователя
🔹 `добавить` - добавить текущего пользователя в избранное
🔹 `избранные` - показать список избранных
🔹 `удалить` - удалить пользователя из избранного
🔹 `помощь` - показать эту справку
🔹 `стоп` - завершить работу

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**⚙️ Как это работает:**

1️⃣ Бот анализирует ваш профиль:
   • Город проживания
   • Возраст
   • Пол

2️⃣ Находит подходящих пользователей для знакомств
   (противоположный пол, ±5 лет от вашего возраста)

3️⃣ Показывает:
   • Имя и фамилию
   • Ссылку на профиль
   • Топ-3 фотографии по лайкам

4️⃣ Вы можете:
   • Сохранять понравившихся в избранное
   • Просматривать список избранных
   • Переходить к следующим кандидатам

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💡 Советы:**

• Добавляйте в избранное тех, кто вам действительно интересен
• Используйте команду 'дальше' для просмотра новых людей
• Ваши избранные сохраняются навсегда (в файле favorites.json)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**❓ Нужна помощь?**

Если у вас возникли проблемы:
• Убедитесь, что ваш профиль не закрыт
• Проверьте, что указали город и дату рождения
• Напишите разработчику: @your_support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 **Приятного общения!** 🎉
        """
        return help_text