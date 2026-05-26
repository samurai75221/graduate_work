import json
from typing import List, Dict


class VKKeyboard:
    """Класс для создания клавиатур ВКонтакте"""

    @staticmethod
    def create_keyboard(buttons: List[List[str]], one_time: bool = False) -> str:
        """
        Создание клавиатуры

        Args:
            buttons: список строк кнопок
            one_time: одноразовая ли клавиатура

        Returns:
            JSON строка с клавиатурой
        """
        keyboard = {
            "one_time": one_time,
            "buttons": []
        }

        for row in buttons:
            keyboard_row = []
            for button_text in row:
                # Определяем цвет кнопки в зависимости от текста
                color = "primary"  # Синяя кнопка по умолчанию

                if "❤️" in button_text or "⭐" in button_text or "добавить" in button_text:
                    color = "positive"  # Зеленая кнопка
                elif "🚫" in button_text or "🗑️" in button_text or "удалить" in button_text:
                    color = "negative"  # Красная кнопка
                elif "Дальше" in button_text or "дальше" in button_text:
                    color = "primary"  # Синяя кнопка

                keyboard_row.append({
                    "action": {
                        "type": "text",
                        "label": button_text
                    },
                    "color": color
                })
            keyboard["buttons"].append(keyboard_row)

        return json.dumps(keyboard, ensure_ascii=False)

    @staticmethod
    def get_main_keyboard() -> str:
        """Получить главную клавиатуру"""
        from config import KeyboardConfig
        return VKKeyboard.create_keyboard(KeyboardConfig.MAIN_MENU)

    @staticmethod
    def get_action_keyboard() -> str:
        """Получить клавиатуру действий с пользователем"""
        from config import KeyboardConfig
        return VKKeyboard.create_keyboard(KeyboardConfig.ACTION_MENU)

    @staticmethod
    def get_favorites_keyboard() -> str:
        """Получить клавиатуру управления избранными"""
        from config import KeyboardConfig
        return VKKeyboard.create_keyboard(KeyboardConfig.FAVORITES_MENU)

    @staticmethod
    def remove_keyboard() -> str:
        """Убрать клавиатуру"""
        return json.dumps({
            "one_time": False,
            "buttons": []
        })