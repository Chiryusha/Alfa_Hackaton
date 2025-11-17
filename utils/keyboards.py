from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура с основными функциями"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📱 Пост для соцсетей"),
                KeyboardButton(text="📝 Коммерческое предложение")
            ],
            [
                KeyboardButton(text="🛍️ Описание товара/услуги"),
                KeyboardButton(text="💼 Консультация")
            ],
            [
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard


def get_content_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа контента"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 Пост", callback_data="content_post"),
                InlineKeyboardButton(text="📝 КП", callback_data="content_offer")
            ],
            [
                InlineKeyboardButton(text="🛍️ Товар/Услуга", callback_data="content_product")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back")
            ]
        ]
    )
    return keyboard


def get_platform_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора платформы соцсетей"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📷 Instagram", callback_data="platform_instagram"),
                InlineKeyboardButton(text="🔵 ВКонтакте", callback_data="platform_vk")
            ],
            [
                InlineKeyboardButton(text="✈️ Telegram", callback_data="platform_telegram"),
                InlineKeyboardButton(text="📘 Facebook", callback_data="platform_facebook")
            ],
            [
                InlineKeyboardButton(text="👥 Одноклассники", callback_data="platform_ok")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back")
            ]
        ]
    )
    return keyboard


def get_consultation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа консультации"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚖️ Юридические", callback_data="consult_legal"),
                InlineKeyboardButton(text="📊 Маркетинг", callback_data="consult_marketing")
            ],
            [
                InlineKeyboardButton(text="💰 Финансы", callback_data="consult_finance"),
                InlineKeyboardButton(text="❓ Другие", callback_data="consult_other")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back")
            ]
        ]
    )
    return keyboard


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Простая клавиатура с кнопкой "Назад" """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back")
            ]
        ]
    )
    return keyboard

