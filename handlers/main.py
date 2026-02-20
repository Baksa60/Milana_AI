from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from models.user import User
from utils.keyboards import get_main_menu
from utils.llm_client import llm_client

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    async with get_async_session() as db:
        # Создаем или получаем пользователя
        user = await db.get(User, message.from_user.id)
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            db.add(user)
            await db.commit()
        
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "Я — твой личный AI-помощник Milana! 🤖\n\n"
            "Что я умею:\n"
            "📊 Отслеживать твои привычки\n"
            "📰 Присылать краткие новости\n"
            "🔮 Генерировать гороскопы\n"
            "💳 Напоминать о подписках\n"
            "⚙️ Настраивать уведомления\n\n"
            "Бесплатный лимит: 5 AI-запросов в день 🎯\n\n"
            "Выбери действие в меню ниже:",
            reply_markup=get_main_menu()
        )
        
        # Сбрасываем состояние FSM
        await state.clear()

@router.message(F.text == "🏠 Главное меню")
@router.message(Command("menu"))
async def show_main_menu(message: types.Message):
    """Показать главное меню"""
    await message.answer(
        "🏠 Главное меню:\n\n"
        "Выбери нужный раздел:",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "📈 Статистика")
async def show_statistics(message: types.Message):
    """Показать статистику пользователя"""
    async with get_async_session() as db:
        user = await db.get(User, message.from_user.id)
        if not user:
            await message.answer("❌ Сначала начните с команды /start")
            return
        
        # Получаем статистику по привычкам
        from models.habit import Habit, HabitRecord
        from sqlalchemy import func, select
        
        habits_query = select(func.count(Habit.id)).where(Habit.user_id == user.id, Habit.is_active == True)
        total_habits = await db.scalar(habits_query)
        
        records_query = select(func.count(HabitRecord.id)).join(Habit).where(Habit.user_id == user.id)
        total_completions = await db.scalar(records_query)
        
        # Получаем статистику по подпискам
        from models.subscription import Subscription
        subs_query = select(func.count(Subscription.id)).where(Subscription.user_id == user.id, Subscription.is_active == True)
        total_subscriptions = await db.scalar(subs_query)
        
        # Считаем месячные расходы
        monthly_query = select(func.sum(Subscription.price)).where(
            Subscription.user_id == user.id, 
            Subscription.is_active == True,
            Subscription.billing_cycle == 'monthly'
        )
        monthly_expenses = await db.scalar(monthly_query) or 0
        
        stats_text = (
            f"📊 Твоя статистика:\n\n"
            f"🔹 Привычки: {total_habits or 0} активных\n"
            f"🔹 Выполнено: {total_completions or 0} раз\n"
            f"🔹 Подписки: {total_subscriptions or 0} активных\n"
            f"🔹 Расходы в месяц: {monthly_expenses:.0f}₽\n\n"
            f"🤖 AI-статистика:\n"
            f"🔹 Сегодня использовано: {user.daily_ai_requests}/5 запросов\n"
            f"🔹 Всего запросов: {user.total_ai_requests}"
        )
        
        await message.answer(stats_text, reply_markup=get_main_menu())

@router.message(F.text == "ℹ️ О боте")
@router.message(Command("about"))
async def show_about(message: types.Message):
    """Информация о боте"""
    about_text = (
        "🤖 <b>Milana AI Bot</b>\n\n"
        "Версия: 1.0.0\n\n"
        "🌟 Возможности:\n"
        "• Трекер привычек с системой стриков\n"
        "• AI-гороскопы на каждый день\n"
        "• Умный агрегатор новостей\n"
        "• Менеджер подписок с напоминаниями\n"
        "• Персональные уведомления\n\n"
        "💰 Бесплатный лимит: 5 AI-запросов в день\n"
        "🔧 Технологии: Python, aiogram 3.x, PostgreSQL, OpenRouter\n\n"
        "👨‍💻 Разработано с любовью к коду ❤️"
    )
    
    await message.answer(about_text, reply_markup=get_main_menu())

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Показать справку"""
    help_text = (
        "📚 <b>Справка по командам:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/menu - Показать главное меню\n"
        "/stats - Статистика использования\n"
        "/help - Эта справка\n"
        "/cancel - Отменить текущее действие\n\n"
        "💡 <b>Советы:</b>\n"
        "• Используй кнопки меню для навигации\n"
        "• AI-запросы ограничены: 5 в день бесплатно\n"
        "• Настройте время уведомлений в настройках\n"
        "• Добавляйте привычки и отслеживайте прогресс!"
    )
    
    await message.answer(help_text, reply_markup=get_main_menu())

@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Отменить текущее действие"""
    await state.clear()
    await message.answer(
        "❌ Действие отменено\n\n"
        "Возвращаю в главное меню:",
        reply_markup=get_main_menu()
    )

@router.message()
async def unknown_message(message: types.Message):
    """Обработчик неизвестных сообщений"""
    if message.text and not message.text.startswith('/'):
        await message.answer(
            "😕 Я не понял эту команду\n\n"
            "Используй кнопки меню или введи /help для справки",
            reply_markup=get_main_menu()
        )
