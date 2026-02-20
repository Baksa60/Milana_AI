from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional

# Главное меню
def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Трекер привычек"),
                KeyboardButton(text="📰 Новости")
            ],
            [
                KeyboardButton(text="🔮 Гороскоп"),
                KeyboardButton(text="💳 Подписки")
            ],
            [
                KeyboardButton(text="⚙️ Настройки"),
                KeyboardButton(text="📈 Статистика")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard

# Клавиатуры для трекера привычек
def get_habits_menu(habits: List[tuple]) -> InlineKeyboardMarkup:
    """Меню управления привычками"""
    builder = InlineKeyboardBuilder()
    
    if habits:
        for habit_id, habit_name, streak in habits:
            builder.row(
                InlineKeyboardButton(
                    text=f"✅ {habit_name} ({streak} дней)",
                    callback_data=f"habit_complete_{habit_id}"
                )
            )
    
    builder.row(
        InlineKeyboardButton(text="➕ Добавить привычку", callback_data="habit_add"),
        InlineKeyboardButton(text="🗑️ Удалить привычку", callback_data="habit_delete")
    )
    
    return builder.as_markup()

def get_habit_confirmation(habit_id: int, habit_name: str) -> InlineKeyboardMarkup:
    """Подтверждение выполнения привычки"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"✅ Я сделал(а) это!",
            callback_data=f"habit_confirm_{habit_id}"
        )
    )
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="habits_menu"))
    return builder.as_markup()

# Клавиатуры для гороскопа
def get_zodiac_signs() -> InlineKeyboardMarkup:
    """Выбор знака зодиака"""
    zodiac_signs = [
        ("♈ Овен", "aries"), ("♉ Телец", "taurus"), ("♊ Близнецы", "gemini"),
        ("♋ Рак", "cancer"), ("♌ Лев", "leo"), ("♍ Дева", "virgo"),
        ("♎ Весы", "libra"), ("♏ Скорпион", "scorpio"), ("♐ Стрелец", "sagittarius"),
        ("♑ Козерог", "capricorn"), ("♒ Водолей", "aquarius"), ("♓ Рыбы", "pisces")
    ]
    
    builder = InlineKeyboardBuilder()
    
    # Разделим на 2 колонки для компактности
    for i in range(0, len(zodiac_signs), 2):
        row_buttons = []
        for sign_text, sign_callback in zodiac_signs[i:i+2]:
            row_buttons.append(
                InlineKeyboardButton(text=sign_text, callback_data=f"horoscope_{sign_callback}")
            )
        builder.row(*row_buttons)
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return builder.as_markup()

# Клавиатуры для подписок
def get_subscriptions_menu(subscriptions: List[tuple]) -> InlineKeyboardMarkup:
    """Меню управления подписками"""
    builder = InlineKeyboardBuilder()
    
    if subscriptions:
        for sub_id, name, price, days_left in subscriptions:
            status_emoji = "🟢" if days_left > 0 else "🔴"
            builder.row(
                InlineKeyboardButton(
                    text=f"{status_emoji} {name} - {price}₽ ({days_left} дней)",
                    callback_data=f"subscription_info_{sub_id}"
                )
            )
    
    builder.row(
        InlineKeyboardButton(text="➕ Добавить подписку", callback_data="subscription_add"),
        InlineKeyboardButton(text="🗑️ Удалить подписку", callback_data="subscription_delete")
    )
    
    return builder.as_markup()

# Клавиатуры для новостей
def get_news_categories() -> InlineKeyboardMarkup:
    """Выбор категории новостей"""
    categories = [
        ("💻 IT", "it"),
        ("₿ Криптовалюты", "crypto"), 
        ("⚽ Спорт", "sports"),
        ("🌍 Мир", "world"),
        ("📈 Бизнес", "business")
    ]
    
    builder = InlineKeyboardBuilder()
    
    for category_text, category_callback in categories:
        builder.row(
            InlineKeyboardButton(
                text=category_text,
                callback_data=f"news_category_{category_callback}"
            )
        )
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return builder.as_markup()

# Клавиатуры для настроек
def get_settings_menu(user_settings: dict) -> InlineKeyboardMarkup:
    """Меню настроек"""
    builder = InlineKeyboardBuilder()
    
    # Уведомления
    notif_status = "🔔 Вкл" if user_settings.get("notifications", True) else "🔕 Выкл"
    builder.row(
        InlineKeyboardButton(
            text=f"Уведомления: {notif_status}",
            callback_data="settings_toggle_notifications"
        )
    )
    
    # Время уведомлений
    notif_time = user_settings.get("notification_time", "09:00")
    builder.row(
        InlineKeyboardButton(
            text=f"⏰ Время уведомлений: {notif_time}",
            callback_data="settings_set_time"
        )
    )
    
    # Часовой пояс
    timezone = user_settings.get("timezone", "UTC")
    builder.row(
        InlineKeyboardButton(
            text=f"🌍 Часовой пояс: {timezone}",
            callback_data="settings_set_timezone"
        )
    )
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return builder.as_markup()

# Универсальная клавиатура подтверждения
def get_confirmation_keyboard(action: str, item_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Универсальная клавиатура для подтверждения действий"""
    builder = InlineKeyboardBuilder()
    
    confirm_data = f"confirm_{action}"
    if item_id is not None:
        confirm_data += f"_{item_id}"
    
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=confirm_data),
        InlineKeyboardButton(text="❌ Нет", callback_data="cancel")
    )
    
    return builder.as_markup()

# Клавиатура отмены действия
def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для отмены действия"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()