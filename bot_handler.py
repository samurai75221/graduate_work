import random
from typing import Dict, List, Optional, Tuple
from vk_client import VKClient
from storage import Storage
from keyboards import VKKeyboard


class DatingBot:
    """Бот для знакомств"""

    # Словарь для отслеживания состояния пользователя
    user_states = {}

    def __init__(self, vk_client: VKClient, storage: Storage):
        """Инициализация бота"""
        self.vk = vk_client
        self.storage = storage
        self.user_search_results = {}  # Кэш результатов поиска для каждого пользователя
        self.user_current_index = {}  # Текущий индекс просматриваемого пользователя
        self.user_photo_attachments = {}  # Кэш фото для аттачей

    def handle_message(self, user_id: int, message: str) -> Optional[Tuple[str, str]]:
        """
        Обработка входящего сообщения

        Args:
            user_id: ID пользователя
            message: текст сообщения

        Returns:
            Кортеж (текст_ответа, клавиатура) или None
        """
        message_lower = message.lower().strip()

        # Обработка команд
        if message_lower in ['начать поиск', '🔍 начать поиск', 'start']:
            return self._start_search(user_id)
        elif message_lower in ['дальше', '➡️ дальше', 'next', 'следующий']:
            return self._get_next_user(user_id)
        elif message_lower in ['добавить в избранное', '⭐ добавить в избранное', 'save']:
            return self._add_current_to_favorites(user_id)
        elif message_lower in ['избранные', '❤️ мои избранные', 'favorites']:
            return self._show_favorites(user_id)
        elif message_lower in ['показать избранных', '📋 показать избранных']:
            return self._show_favorites(user_id)
        elif message_lower in ['удалить из избранного', '🗑️ удалить из избранного']:
            return self._show_favorites_for_deletion(user_id)
        elif message_lower in ['помощь', '📋 помощь', 'help']:
            return self._show_help()
        elif message_lower in ['стоп', '🚪 стоп', 'exit', 'главное меню', '🏠 главное меню']:
            return self._show_main_menu()
        elif message_lower in ['пропустить', '🚫 пропустить']:
            return self._skip_user(user_id)
        elif message_lower.startswith('del_'):
            return self._delete_favorite_by_id(user_id, message)

        # Если пользователь в режиме удаления, обрабатываем ID
        if self.user_states.get(user_id) == 'deleting':
            try:
                fav_id = int(message)
                return self._delete_favorite_by_id(user_id, fav_id)
            except ValueError:
                return self._show_favorites_for_deletion(user_id)

        return self._show_help()

    def _start_search(self, user_id: int) -> Tuple[str, str]:
        """Начало поиска пользователей"""
        # Получаем информацию о пользователе
        user_info = self.vk.get_user_info(user_id)
        if not user_info:
            return ("❌ Не удалось получить информацию о вас. "
                    "Пожалуйста, проверьте настройки приватности.",
                    VKKeyboard.get_main_keyboard())

        # Определяем возраст
        age = self.vk.calculate_age(user_info.get('bdate', ''))
        if not age:
            age_from, age_to = 20, 30
        else:
            age_from, age_to = max(18, age - 5), min(99, age + 5)

        # Поиск пользователей
        city = user_info.get('city', '')
        if not city:
            city = "Москва"

        users = self.vk.search_users(city, age_from, age_to, user_info['sex'])

        # Фильтруем черный список
        users = [u for u in users if not self.storage.is_blacklisted(u['id'])]

        if not users:
            return ("😔 К сожалению, не удалось найти пользователей по вашим критериям. "
                    "Попробуйте позже или измените параметры.",
                    VKKeyboard.get_main_keyboard())

        # Сохраняем результаты поиска
        self.user_search_results[user_id] = users
        self.user_current_index[user_id] = 0

        # Получаем фото для первого пользователя
        user = users[0]
        photo_attachments = self.vk.get_photo_attachments(user['id'])
        self.user_photo_attachments[user_id] = photo_attachments

        message = self._format_user_message(user)
        return (message, VKKeyboard.get_action_keyboard())

    def _get_next_user(self, user_id: int) -> Tuple[str, str]:
        """Получение следующего пользователя"""
        if user_id not in self.user_search_results:
            return ("🔍 Сначала начните поиск командой 'Начать поиск'.",
                    VKKeyboard.get_main_keyboard())

        users = self.user_search_results[user_id]
        current_index = self.user_current_index.get(user_id, 0)

        if current_index + 1 >= len(users):
            # Поиск новых пользователей
            return self._start_search(user_id)

        self.user_current_index[user_id] = current_index + 1
        user = users[current_index + 1]

        # Получаем фото для нового пользователя
        photo_attachments = self.vk.get_photo_attachments(user['id'])
        self.user_photo_attachments[user_id] = photo_attachments

        message = self._format_user_message(user)
        return (message, VKKeyboard.get_action_keyboard())

    def _skip_user(self, user_id: int) -> Tuple[str, str]:
        """Пропустить текущего пользователя (добавить в черный список)"""
        current_user = self._get_current_user(user_id)
        if not current_user:
            return ("Нет текущего пользователя для пропуска.",
                    VKKeyboard.get_action_keyboard())

        # Добавляем в черный список
        self.storage.add_to_blacklist(current_user['id'])

        # Показываем следующего
        return self._get_next_user(user_id)

    def _add_current_to_favorites(self, user_id: int) -> Tuple[str, str]:
        """Добавление текущего пользователя в избранное"""
        current_user = self._get_current_user(user_id)
        if not current_user:
            return ("❌ Нет текущего пользователя для добавления.",
                    VKKeyboard.get_main_keyboard())

        # Добавляем фотографии к данным пользователя
        photos = self.vk.get_user_photos(current_user['id'])
        current_user['photos'] = [photo[0] for photo in photos]
        current_user['photos_likes'] = [photo[1] for photo in photos]

        if self.storage.add_to_favorites(current_user):
            message = (f"✅ {current_user['first_name']} {current_user['last_name']} "
                       f"добавлен(а) в избранное!")
        else:
            message = (f"⚠️ {current_user['first_name']} {current_user['last_name']} "
                       f"уже в избранном.")

        # Автоматически показываем следующего пользователя
        return (message + "\n\n" + self._get_next_user(user_id)[0],
                VKKeyboard.get_action_keyboard())

    def _show_favorites(self, user_id: int) -> Tuple[str, str]:
        """Показ списка избранных"""
        favorites = self.storage.get_favorites()

        if not favorites:
            return ("💔 Ваш список избранных пока пуст.\n"
                    "Начните поиск и добавляйте понравившихся людей!",
                    VKKeyboard.get_main_keyboard())

        message = "💖 **Ваш список избранных** 💖\n\n"
        for i, fav in enumerate(favorites, 1):
            message += f"{i}. 👤 {fav['first_name']} {fav['last_name']}\n"
            message += f"   🔗 {fav['profile_url']}\n"
            message += f"   📅 Добавлен: {fav.get('added_at', 'Неизвестно')[:10]}\n\n"

        return (message, VKKeyboard.get_favorites_keyboard())

    def _show_favorites_for_deletion(self, user_id: int) -> Tuple[str, str]:
        """Показать список избранных для удаления"""
        favorites = self.storage.get_favorites()

        if not favorites:
            return ("📭 Список избранных пуст. Нечего удалять.",
                    VKKeyboard.get_main_keyboard())

        message = "🗑️ **Выберите пользователя для удаления**\n\n"
        for i, fav in enumerate(favorites, 1):
            message += f"{i}. {fav['first_name']} {fav['last_name']}\n"
            message += f"   ID: {fav['id']}\n\n"

        message += "Отправьте ID пользователя для удаления из избранного:"

        # Сохраняем состояние пользователя
        self.user_states[user_id] = 'deleting'

        return (message, VKKeyboard.get_favorites_keyboard())

    def _delete_favorite_by_id(self, user_id: int, fav_id) -> Tuple[str, str]:
        """Удаление пользователя из избранного по ID"""
        try:
            if isinstance(fav_id, str):
                if fav_id.startswith('del_'):
                    fav_id = int(fav_id[4:])
                else:
                    fav_id = int(fav_id)
        except ValueError:
            return ("❌ Пожалуйста, отправьте корректный ID пользователя.",
                    VKKeyboard.get_favorites_keyboard())

        # Поиск и удаление
        favorites = self.storage.get_favorites()
        user_to_delete = None

        for fav in favorites:
            if fav['id'] == fav_id:
                user_to_delete = fav
                break

        if user_to_delete:
            self.storage.remove_from_favorites(fav_id)
            # Сбрасываем состояние
            self.user_states.pop(user_id, None)
            return (f"✅ {user_to_delete['first_name']} {user_to_delete['last_name']} "
                    f"удален(а) из избранного.",
                    VKKeyboard.get_main_keyboard())
        else:
            return ("❌ Пользователь с таким ID не найден в избранном.",
                    VKKeyboard.get_favorites_keyboard())

    def _get_current_user(self, user_id: int) -> Optional[Dict]:
        """Получение текущего просматриваемого пользователя"""
        if user_id not in self.user_search_results:
            return None

        users = self.user_search_results[user_id]
        current_index = self.user_current_index.get(user_id, 0)

        if current_index < len(users):
            return users[current_index]
        return None

    def _format_user_message(self, user: Dict) -> str:
        """Форматирование сообщения о пользователе"""
        message = (
            f"🎯 **Найден пользователь** 🎯\n\n"
            f"👤 **{user['first_name']} {user['last_name']}**\n"
            f"🏙️ **Город:** {user.get('city', 'Не указан')}\n"
            f"🔗 **Ссылка:** {user['profile_url']}\n\n"
            f"📸 **Топ фотографии:**\n"
        )

        return message

    def _show_help(self) -> Tuple[str, str]:
        """Показ справки"""
        help_text = """
🤖 **Бот для знакомств ВКонтакте** 🤖

**📋 Доступные команды:**

🔹 `Начать поиск` - начать подбор пользователей
🔹 `Дальше` - показать следующего пользователя
🔹 `Добавить в избранное` - сохранить текущего в избранное
🔹 `Мои избранные` - показать список избранных
🔹 `Удалить из избранного` - удалить пользователя
🔹 `Пропустить` - пропустить и больше не показывать
🔹 `Помощь` - показать эту справку
🔹 `Главное меню` - вернуться в главное меню

**✨ Как это работает:**
1. Бот анализирует ваш профиль (город, возраст, пол)
2. Находит подходящих пользователей для знакомств
3. Показывает фото, имя и ссылку на профиль
4. Вы можете добавлять понравившихся в избранное

**💡 Совет:** Используйте кнопки для удобного управления!

Приятного общения! 💝
        """
        return (help_text, VKKeyboard.get_main_keyboard())

    def _show_main_menu(self) -> Tuple[str, str]:
        """Показать главное меню"""
        # Очищаем состояние пользователя
        self.user_states.pop(user_id, None) if hasattr(self, 'user_states') else None

        return ("🏠 **Главное меню**\n\n"
                "Выберите действие с помощью кнопок ниже:",
                VKKeyboard.get_main_keyboard())