"""Главный модуль для запуска бота"""

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import VK_GROUP_TOKEN, VK_GROUP_ID
from vk_client import VKClient
from storage import Storage
from bot_handler import DatingBot
from keyboards import VKKeyboard


def main():
    """Основная функция запуска бота"""
    print("🤖 Запуск бота для знакомств ВКонтакте...")
    print("=" * 50)



    # Инициализация компонентов
    vk_client = VKClient(VK_GROUP_TOKEN)
    storage = Storage()
    bot = DatingBot(vk_client, storage)

    # Настройка long poll для бота
    try:
        vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
        longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)

        print("✅ Бот успешно запущен!")
        print(f"📱 ID группы: {VK_GROUP_ID}")
        print("💬 Бот ожидает сообщения...")
        print("=" * 50)

        # Отправляем приветственное сообщение
        print("\n💡 Совет: Отправьте любое сообщение боту в личные сообщения группы")
        print("   Бот ответит с кнопками для управления.\n")

        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                try:
                    user_id = event.object.message['from_id']
                    message_text = event.object.message.get('text', '')

                    # Получаем ответ от бота
                    result = bot.handle_message(user_id, message_text)

                    if result:
                        response_text, keyboard_json = result
                        # Отправка ответа с клавиатурой
                        vk_client.send_message(
                            user_id,
                            response_text,
                            keyboard=keyboard_json
                        )

                    # Вывод в консоль для отладки
                    print(f"📨 Сообщение от {user_id}: {message_text[:50]}")

                except Exception as e:
                    print(f"❌ Ошибка при обработке сообщения: {e}")
                    try:
                        vk_client.send_message(
                            user_id,
                            "❌ Произошла ошибка. Пожалуйста, попробуйте позже.",
                            keyboard=VKKeyboard.get_main_keyboard()
                        )
                    except:
                        pass
                    continue

    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("\n🔧 Возможные причины:")
        print("1. Неправильный токен доступа")
        print("2. Неправильный ID группы")
        print("3. Отсутствуют необходимые права доступа у токена")
        print("\n📖 Инструкция по настройке в README.md")


if __name__ == "__main__":
    main()