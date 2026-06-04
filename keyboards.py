"""Модуль для создания клавиатур бота"""

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import KeyboardConfig


class Keyboards:
    """Класс для создания клавиатур"""

    @staticmethod
    def get_main_keyboard() -> VkKeyboard:
        """
        Главная клавиатура с основными командами

        Returns:
            VkKeyboard: объект клавиатуры
        """
        keyboard = VkKeyboard(one_time=False)

        # Первый ряд
        keyboard.add_button(KeyboardConfig.BTN_START, color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(KeyboardConfig.BTN_NEXT, color=VkKeyboardColor.PRIMARY)

        # Второй ряд
        keyboard.add_line()
        keyboard.add_button(KeyboardConfig.BTN_FAVORITE, color=VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyboardConfig.BTN_FAVORITES, color=VkKeyboardColor.PRIMARY)

        # Третий ряд
        keyboard.add_line()
        keyboard.add_button(KeyboardConfig.BTN_HELP, color=VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyboardConfig.BTN_STOP, color=VkKeyboardColor.NEGATIVE)

        return keyboard

    @staticmethod
    def get_search_keyboard() -> VkKeyboard:
        """
        Клавиатура для режима поиска

        Returns:
            VkKeyboard: объект клавиатуры
        """
        keyboard = VkKeyboard(one_time=False)

        keyboard.add_button(KeyboardConfig.BTN_NEXT, color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(KeyboardConfig.BTN_FAVORITE, color=VkKeyboardColor.POSITIVE)

        keyboard.add_line()
        keyboard.add_button(KeyboardConfig.BTN_FAVORITES, color=VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyboardConfig.BTN_STOP, color=VkKeyboardColor.NEGATIVE)

        return keyboard

    @staticmethod
    def get_favorites_keyboard() -> VkKeyboard:
        """
        Клавиатура для режима просмотра избранных

        Returns:
            VkKeyboard: объект клавиатуры
        """
        keyboard = VkKeyboard(one_time=False)

        keyboard.add_button(KeyboardConfig.BTN_NEXT, color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(KeyboardConfig.BTN_FAVORITE, color=VkKeyboardColor.POSITIVE)

        keyboard.add_line()
        keyboard.add_button("🗑️ Удалить", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button(KeyboardConfig.BTN_HELP, color=VkKeyboardColor.SECONDARY)

        return keyboard

    @staticmethod
    def get_simple_keyboard() -> VkKeyboard:
        """
        Простая клавиатура с базовыми кнопками

        Returns:
            VkKeyboard: объект клавиатуры
        """
        keyboard = VkKeyboard(one_time=False)

        keyboard.add_button(KeyboardConfig.BTN_START, color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(KeyboardConfig.BTN_HELP, color=VkKeyboardColor.SECONDARY)

        return keyboard