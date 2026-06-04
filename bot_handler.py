"""Модуль с логикой обработки сообщений бота"""

from typing import Dict, List, Optional, Tuple
from vk_client import VKClient
from storage import Storage
from keyboards import Keyboards
from config import KeyboardConfig


class DatingBot:
    """Бот для знакомств"""

    def __init__(self, vk_client: VKClient, storage: Storage):
        """Инициализация бота"""
        self.vk = vk_client
        self.storage = storage
        self.user_search_results = {}
        self.user_current_index = {}
        self.user_current_photos = {}
        self.user_temp_state = {}  # Для временного состояния (удаление из избранного)

    def handle_message(self, user_id: int, message: str) -> Optional[Tuple[str, object]]:
        """
        Обработка входящего сообщения

        Returns:
            Tuple (текст_ответа, клавиатура) или None
        """
        message_lower = message.lower().strip()

        # Обработка команды удаления с индексом
        if message_lower.startswith('удалить'):
            parts = message.split()
            if len(parts) > 1 and parts[1].isdigit():
                return self._remove_favorite_by_index(user_id, int(parts[1]) - 1)

        # Обработка обычных команд
        if message_lower in ['начать', 'start', 'привет', KeyboardConfig.BTN_START.lower()]:
            return self._start_search(user_id)
        elif message_lower in ['дальше', 'next', 'следующий', KeyboardConfig.BTN_NEXT.lower()]:
            return self._get_next_user(user_id)
        elif message_lower in ['избранные', 'favorites', 'список', KeyboardConfig.BTN_FAVORITES.lower()]:
            return self._show_favorites(user_id)
        elif message_lower in ['добавить', 'save', 'в избранное', KeyboardConfig.BTN_FAVORITE.lower()]:
            return self._add_current_to_favorites(user_id)
        elif message_lower in ['помощь', 'help', '?', KeyboardConfig.BTN_HELP.lower()]:
            return self._show_help()
        elif message_lower in ['стоп', 'stop', 'exit', KeyboardConfig.BTN_STOP.lower()]:
            return self._stop_search(user_id)

        return None

    def _start_search(self, user_id: int) -> Tuple[str, object]:
        """Начало поиска пользователей"""
        user_info = self.vk.get_user_info(user_id)
        if not user_info:
            return ("❌ Не удалось получить информацию о вас. "
                   "Проверьте настройки приватности.",
                   Keyboards.get_simple_keyboard())

        age = self.vk.calculate_age(user_info.get('bdate', ''))
        if not age:
            age_from, age_to = 20, 30
        else:
            age_from, age_to = age - 5, age + 5

        city = user_info.get('city', 'Москва')
        if not city:
            city = "Москва"

        users = self.vk.search_users(city, age_from, age_to, user_info['sex'])
        users = [u for u in users if not self.storage.is_blacklisted(u['vk_id'])]

        if not users:
            return ("😔 К сожалению, не удалось найти пользователей по вашим критериям.\n\n"
                   "Попробуйте позже или измените параметры поиска.",
                   Keyboards.get_simple_keyboard())

        self.user_search_results[user_id] = users
        self.user_current_index[user_id] = 0

        return self._send_user_with_photos(user_id, users[0])

    def _send_user_with_photos(self, user_id: int, user: Dict) -> Tuple[str, object]:
        """
        Формирование сообщения с пользователем и его фотографиями

        Returns:
            Tuple (текст_сообщения, клавиатура)
        """
        # Получаем фотографии
        photos = self.vk.get_user_photos(user['vk_id'])
        self.user_current_photos[user_id] = photos

        # Формируем текст сообщения
        message = f"🎯 **Найден пользователь для знакомств**\n\n"
        message += f"👤 **{user['first_name']} {user['last_name']}**\n"
        message += f"🏙️ Город: {user.get('city', 'Не указан')}\n"
        message += f"🔗 Профиль: {user['profile_url']}\n\n"

        if photos:
            message += f"📸 **Топ {len(photos)} фотографий** (по количеству лайков):\n"
            for i, (_, likes, _) in enumerate(photos, 1):
                message += f"{i}. ❤️ {likes} лайков\n"
        else:
            message += "📸 Фотографии не найдены или профиль закрыт\n"

        message += f"\n💬 **Управление:**"

        # Формируем attachments (вложения с фото)
        attachments = [photo[2] for photo in photos] if photos else []

        # Сохраняем attachments для использования при добавлении в избранное
        if photos:
            user['photos'] = [photo[0] for photo in photos]
            user['photos_attachments'] = attachments
            user['photos_likes'] = [photo[1] for photo in photos]

        # Отправляем сообщение с фото и клавиатурой
        self.vk.send_message(user_id, message, attachments, Keyboards.get_search_keyboard())
        return None  # Сообщение уже отправлено

    def _get_next_user(self, user_id: int) -> Optional[Tuple[str, object]]:
        """Получение следующего пользователя"""
        if user_id not in self.user_search_results:
            return ("🔍 Сначала начните поиск командой 'начать'.",
                   Keyboards.get_simple_keyboard())

        users = self.user_search_results[user_id]
        current_index = self.user_current_index.get(user_id, 0)

        if current_index + 1 >= len(users):
            return self._start_search(user_id)

        self.user_current_index[user_id] = current_index + 1
        next_user = users[current_index + 1]

        return self._send_user_with_photos(user_id, next_user)

    def _add_current_to_favorites(self, user_id: int) -> Tuple[str, object]:
        """Добавление текущего пользователя в избранное"""
        current_user = self._get_current_user(user_id)
        if not current_user:
            return ("❌ Нет текущего пользователя. Начните поиск командой 'начать'.",
                   Keyboards.get_simple_keyboard())

        # Проверяем, есть ли уже в избранном
        favorites = self.storage.load_favorites()
        for fav in favorites:
            if fav.get('vk_id') == current_user['vk_id']:
                return (f"⚠️ **{current_user['first_name']} {current_user['last_name']}** "
                       f"уже в избранном!",
                       Keyboards.get_search_keyboard())

        # Добавляем фотографии к данным пользователя
        photos = self.user_current_photos.get(user_id, [])
        current_user['photos'] = [photo[0] for photo in photos]
        current_user['photos_attachments'] = [photo[2] for photo in photos]
        current_user['photos_likes'] = [photo[1] for photo in photos]

        if self.storage.add_to_favorites(current_user):
            return (f"✅ **{current_user['first_name']} {current_user['last_name']}** "
                   f"добавлен(а) в избранное!\n📸 Сохранено {len(photos)} фотографий.",
                   Keyboards.get_search_keyboard())
        else:
            return (f"❌ Ошибка при добавлении в избранное.",
                   Keyboards.get_search_keyboard())

    def _show_favorites(self, user_id: int) -> Tuple[str, object]:
        """Показ списка избранных"""
        favorites = self.storage.get_favorites()

        if not favorites:
            return ("💔 Список избранных пуст.\n\nНачните поиск командой 'начать'.",
                   Keyboards.get_simple_keyboard())

        response = "💖 **МОИ ИЗБРАННЫЕ** 💖\n\n"
        for i, fav in enumerate(favorites, 1):
            response += f"{i}. **{fav['first_name']} {fav['last_name']}**\n"
            response += f"   🔗 {fav['profile_url']}\n"
            response += f"   📅 Добавлен: {fav.get('saved_at', 'Неизвестно')[:19]}\n"

            if 'photos_likes' in fav and fav['photos_likes']:
                response += f"   📸 {len(fav['photos_likes'])} фото | ❤️ {sum(fav['photos_likes'])} лайков\n"

            response += "\n"

        response += "💡 **Для удаления:** отправьте 'удалить N' (где N - номер в списке)\n"
        response += "💡 **Продолжить поиск:** отправьте 'дальше'"

        return (response, Keyboards.get_favorites_keyboard())

    def _remove_favorite_by_index(self, user_id: int, index: int) -> Tuple[str, object]:
        """Удаление пользователя из избранного по индексу"""
        favorites = self.storage.get_favorites()

        if 0 <= index < len(favorites):
            removed_user = favorites[index]
            if self.storage.remove_favorite_by_index(index):
                return (f"✅ Удален(а) **{removed_user['first_name']} {removed_user['last_name']}** "
                       f"из избранного.",
                       Keyboards.get_simple_keyboard())

        return (f"❌ Неверный номер. Всего в избранном: {len(favorites)} пользователей.\n"
               f"Отправьте 'удалить N', где N - номер из списка.",
               Keyboards.get_favorites_keyboard())

    def _get_current_user(self, user_id: int) -> Optional[Dict]:
        """Получение текущего просматриваемого пользователя"""
        if user_id not in self.user_search_results:
            return None

        users = self.user_search_results[user_id]
        current_index = self.user_current_index.get(user_id, 0)

        if current_index < len(users):
            return users[current_index]
        return None

    def _stop_search(self, user_id: int) -> Tuple[str, object]:
        """Остановка поиска"""
        if user_id in self.user_search_results:
            del self.user_search_results[user_id]
        if user_id in self.user_current_index:
            del self.user_current_index[user_id]
        if user_id in self.user_current_photos:
            del self.user_current_photos[user_id]

        return ("👋 Поиск остановлен.\n\n"
               "Чтобы начать заново, отправьте 'начать'.",
               Keyboards.get_simple_keyboard())

    def _show_help(self) -> Tuple[str, object]:
        """Показ справки"""
        help_text = """
🤖 **БОТ ДЛЯ ЗНАКОМСТВ ВКОНТАКТЕ** 🤖

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📌 Команды:**

🔹 `начать` - начать поиск
🔹 `дальше` - следующий кандидат  
🔹 `добавить` - в избранное
🔹 `избранные` - список избранных
🔹 `удалить N` - удалить N-го из избранных
🔹 `помощь` - эта справка
🔹 `стоп` - завершить поиск

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📱 Как работает:**

1️⃣ Бот анализирует ваш профиль
2️⃣ Находит подходящих кандидатов
3️⃣ Показывает фото и ссылку
4️⃣ Вы сохраняете понравившихся

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 **Приятного общения!** 🎉
        """
        return (help_text, Keyboards.get_main_keyboard())