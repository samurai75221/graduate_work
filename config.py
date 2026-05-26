# Токен группы ВКонтакте
VK_GROUP_TOKEN = "vk1.a.B6MhytLUcnqN_QiJzB7_M-cYyR3K0t4E46OabS2yqK90boAMJ6U2PeEMZ2u8pR3kZ4yOyWlhF6wEIjhMMZLwAb0Fu99REiw157zGFaI4hMmuGOD_IFzD3qeDz6-q9t0875F-CJSlp7kSnqoAEW69jhMp4CTCxU_JKctuJ1dPR_93zdUUelx4WZzOYSzYxNlRAiOaRcoeDJwk4SwKcUZ3WA"

# ID группы (можно найти в управлении сообществом)
VK_GROUP_ID = 238213575

# Версия API VK
VK_API_VERSION = "5.131"

# Количество пользователей для поиска
SEARCH_COUNT = 50

# Количество фотографий для отображения
PHOTOS_COUNT = 3


# Конфигурация кнопок
class KeyboardConfig:
    """Конфигурация клавиатуры бота"""

    # Основное меню
    MAIN_MENU = [
        ["🔍 Начать поиск", "❤️ Избранные"],
        ["📋 Помощь", "🚪 Стоп"]
    ]

    # Меню действий с пользователем
    ACTION_MENU = [
        ["➡️ Дальше", "⭐ Добавить в избранное"],
        ["❤️ Мои избранные", "🚫 Пропустить"],
        ["🏠 Главное меню"]
    ]

    # Меню управления избранными
    FAVORITES_MENU = [
        ["📋 Показать избранных", "🗑️ Удалить из избранного"],
        ["🏠 Главное меню"]
    ]