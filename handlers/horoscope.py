from aiogram import Router, F, types

router = Router()

@router.message(F.text == "🔮 Гороскоп")
async def show_horoscope_menu(message: types.Message):
    """Заглушка для гороскопа"""
    await message.answer(
        "🔮 <b>Гороскоп</b>\n\n"
        "Этот модуль в разработке...\n\n"
        "Скоро здесь будет:\n"
        "• Ежедневные AI-гороскопы\n"
        "• Персональные предсказания\n"
        "• Совместимость знаков",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🏠 Главное меню")]
            ],
            resize_keyboard=True
        )
    )
