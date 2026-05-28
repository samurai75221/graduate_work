"""Конфигурационные параметры бота"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Токен группы ВКонтакте (теперь берется из переменных окружения)
VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")

# ID группы
VK_GROUP_ID = int(os.getenv("VK_GROUP_ID", 0))

# Версия API VK
VK_API_VERSION = "5.131"

# Количество пользователей для поиска
SEARCH_COUNT = 50

# Количество фотографий для отображения
PHOTOS_COUNT = 3