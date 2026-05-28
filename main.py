"""Главный модуль для запуска бота"""

import os
import sys
import time
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import VK_GROUP_TOKEN, VK_GROUP_ID
from vk_client import VKClient
from storage import Storage
from bot_handler import DatingBot


def check_config():
    """Проверка конфигурации перед запуском"""
    if not VK_GROUP_TOKEN or VK_GROUP_TOKEN == "ваш_токен_здесь":
        print("❌ ОШИБКА: Токен ВКонтакте не настроен!")
        print("\n📝 Инструкция по настройке:")
        print("1. Создайте файл .env в корне проекта")
        print("2. Добавьте в него строки:")
        print("   VK_GROUP_TOKEN=ваш_токен")
        print("   VK_GROUP_ID=id_вашей_группы")
        print("\n3. Получить токен можно здесь: https://vkhost.github.io/")
        print("   (нужны права: сообщения, фото, пользователи)")
        return False

    if VK_GROUP_ID == 0:
        print("❌ ОШИБКА: ID группы не настроен!")
        print("Добавьте VK_GROUP_ID в файл .env")
        return False

    return True


def main():
    """Основная функция запуска бота"""
    print("=" * 50)
    print("🤖 ЗАПУСК БОТА ДЛЯ ЗНАКОМСТВ ВКОНТАКТЕ")
    print("=" * 50)

    # Проверка конфигурации
    if not check_config():
        sys.exit(1)

    print("✅ Конфигурация проверена")

    # Инициализация компонентов
    try:
        vk_client = VKClient(VK_GROUP_TOKEN)
        storage = Storage()
        bot = DatingBot(vk_client, storage)

        print("✅ Компоненты инициализированы")

        # Настройка long poll для бота
        vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
        longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)

        print("=" * 50)
        print("✅ БОТ УСПЕШНО ЗАПУЩЕН!")
        print("📨 Ожидаю сообщения от пользователей...")
        print("=" * 50)
        print("💡 Для остановки бота нажмите Ctrl+C")
        print("=" * 50)

        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                try:
                    user_id = event.object.message['from_id']
                    message_text = event.object.message.get('text', '')

                    # Логируем входящее сообщение
                    print(f"📩 Сообщение от {user_id}: {message_text[:50]}")

                    # Обработка сообщения
                    response = bot.handle_message(user_id, message_text)

                    if response:
                        # Отправка ответа
                        vk_client.send_message(user_id, response)
                        print(f"📤 Ответ отправлен пользователю {user_id}")

                except Exception as e:
                    print(f"❌ Ошибка при обработке сообщения: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("🛑 Бот остановлен пользователем")
        print("👋 До свидания!")
        print("=" * 50)

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("\nВозможные причины:")
        print("• Неправильный токен доступа")
        print("• Недостаточно прав у токена")
        print("• Проблемы с подключением к интернету")
        print("\nПроверьте настройки в файле .env и попробуйте снова.")
        sys.exit(1)


if __name__ == "__main__":
    main()