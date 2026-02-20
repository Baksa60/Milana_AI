from aiogram import Router, F, types

router = Router(name="settings")

@router.message(F.text == "⚙️ Настройки")
async def show_settings_menu(message: types.Message):
    """Заглушка для настроек"""
    print(f"🔍 DEBUG: Настройки - получено сообщение: '{message.text}'")
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Этот модуль в разработке...\n\n"
        "Скоро здесь будет:\n"
        "• Управление уведомлениями\n"
        "• Настройка времени рассылок\n"
        "• Выбор часового пояса\n"
        "• Персонализация бота",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🏠 Главное меню")]
            ],
            resize_keyboard=True
        )
    )
