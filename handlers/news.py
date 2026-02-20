from aiogram import Router, F, types

router = Router(name="news")

@router.message(F.text == "📰 Новости")
async def show_news_menu(message: types.Message):
    """Заглушка для новостей"""
    await message.answer(
        "📰 <b>Умный агрегатор новостей</b>\n\n"
        "Этот модуль в разработке...\n\n"
        "Скоро здесь будет:\n"
        "• AI-саммари новостей\n"
        "• Персональные дайджесты\n"
        "• Категории: IT, крипта, спорт\n"
        "• Ежедневные рассылки",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🏠 Главное меню")]
            ],
            resize_keyboard=True
        )
    )
