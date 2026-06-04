"""Главный модуль для запуска бота"""

import sys
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import VK_GROUP_TOKEN, VK_GROUP_ID
from vk_client import VKClient
from storage import Storage
from bot_handler import DatingBot
from keyboards import Keyboards


def check_config():
    """Проверка конфигурации перед запуском"""
    if not VK_GROUP_TOKEN or VK_GROUP_TOKEN == "ваш_токен_здесь":
        print("❌ ОШИБКА: Токен ВКонтакте не настроен!")
        print("\n📝 Инструкция по настройке:")
        print("1. Скопируйте .env.example в .env")
        print("2. Отредактируйте .env, добавив ваш токен и ID группы")
        print("3. Получить токен можно на https://vkhost.github.io/")
        return False

    if VK_GROUP_ID == 0:
        print("❌ ОШИБКА: ID группы не настроен!")
        return False

    return True


def main():
    """Основная функция запуска бота"""
    print("=" * 50)
    print("🤖 ЗАПУСК БОТА ДЛЯ ЗНАКОМСТВ ВКОНТАКТЕ")
    print("=" * 50)

    if not check_config():
        sys.exit(1)

    print("✅ Конфигурация проверена")

    try:
        vk_client = VKClient(VK_GROUP_TOKEN)
        storage = Storage()
        bot = DatingBot(vk_client, storage)

        vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
        longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)

        print("✅ БОТ УСПЕШНО ЗАПУЩЕН!")
        print("📨 Ожидаю сообщения от пользователей...")
        print("=" * 50)
        print("💡 Для остановки нажмите Ctrl+C")
        print("=" * 50)

        # Отправляем приветственное сообщение с клавиатурой
        welcome_message = ("👋 Привет! Я бот для знакомств ВКонтакте!\n\n"
                          "🔍 Я помогу найти интересных людей для общения.\n\n"
                          "💡 Нажмите 'Начать поиск' или отправьте команду 'начать'.")

        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                try:
                    user_id = event.object.message['from_id']
                    message_text = event.object.message.get('text', '')

                    # Проверяем, не первое ли сообщение от пользователя
                    if message_text.lower() in ['начать', 'start', 'привет'] or not message_text:
                        # Отправляем приветствие с клавиатурой
                        vk_client.send_message(user_id, welcome_message,
                                              keyboard=Keyboards.get_main_keyboard())
                        continue

                    print(f"📩 Сообщение от {user_id}: {message_text[:50]}")

                    result = bot.handle_message(user_id, message_text)

                    if result:
                        response_text, keyboard = result
                        vk_client.send_message(user_id, response_text, keyboard=keyboard)
                        print(f"📤 Ответ отправлен с клавиатурой")

                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("🛑 Бот остановлен")
        print("👋 До свидания!")

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()