from aiogram import Router, F, types

router = Router(name="subscriptions")

@router.message(F.text == "💳 Подписки")
async def show_subscriptions_menu(message: types.Message):
    """Заглушка для подписок"""
    await message.answer(
        "💳 <b>Менеджер подписок</b>\n\n"
        "Этот модуль в разработке...\n\n"
        "Скоро здесь будет:\n"
        "• Отслеживание подписок\n"
        "• Напоминания о платежах\n"
        "• Аналитика расходов\n"
        "• Уведомления о триалах",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🏠 Главное меню")]
            ],
            resize_keyboard=True
        )
    )
