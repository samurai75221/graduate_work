"""Конфигурационные параметры бота"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Токен группы ВКонтакте
VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")

# ID группы
VK_GROUP_ID = int(os.getenv("VK_GROUP_ID", 0))

# Версия API VK
VK_API_VERSION = "5.131"

# Количество пользователей для поиска
SEARCH_COUNT = 50

# Количество фотографий для отображения
PHOTOS_COUNT = 3


class KeyboardConfig:
    """Конфигурация клавиатуры бота"""

    # Цвета кнопок
    PRIMARY = "primary"
    SECONDARY = "secondary"
    NEGATIVE = "negative"
    POSITIVE = "positive"

    # Основные кнопки
    BTN_START = "🔍 Начать поиск"
    BTN_NEXT = "➡️ Дальше"
    BTN_FAVORITE = "❤️ В избранное"
    BTN_FAVORITES = "📋 Избранные"
    BTN_HELP = "❓ Помощь"
    BTN_STOP = "⏹️ Стоп"