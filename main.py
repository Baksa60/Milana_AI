"""
Упрощенная версия основного бота
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///data/milana.db'

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime

from core.database import get_async_session, init_db
from models.user import User
from models.habit import Habit, HabitRecord
from utils.keyboards import get_main_menu, get_habits_menu, get_habit_confirmation, get_cancel_keyboard

# Создаем роутер
router = Router()

class HabitStates(StatesGroup):
    adding_name = State()

async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()

# Основные команды
@router.message(F.text == "/start")
async def start_cmd(message: types.Message, state: FSMContext):
    async with get_async_session() as db:
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
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
        await state.clear()

@router.message(F.text == "/help")
async def help_cmd(message: types.Message):
    await message.answer(
        "📚 <b>Справка по командам:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Эта справка\n\n"
        "💡 <b>Советы:</b>\n"
        "• Используй кнопки меню для навигации\n"
        "• AI-запросы ограничены: 5 в день бесплатно",
        reply_markup=get_main_menu()
    )

# Кнопки главного меню
@router.message(F.text == "📊 Трекер привычек")
async def habits_cmd(message: types.Message):
    async with get_async_session() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
        if not user:
            await message.answer("❌ Сначала начните с команды /start")
            return
        
        query = select(
            Habit.id, 
            Habit.name, 
            Habit.current_streak
        ).where(
            and_(Habit.user_id == user.id, Habit.is_active == True)
        ).order_by(Habit.created_at)
        
        result = await db.execute(query)
        habits = result.all()
        
        if not habits:
            await message.answer(
                "📊 У тебя пока нет привычек\n\n"
                "Добавь первую привычку, чтобы начать отслеживать прогресс!",
                reply_markup=get_habits_menu([])
            )
        else:
            text = f"📊 Твои привычки ({len(habits)}):\n\n"
            habits_list = []
            for habit_id, habit_name, streak in habits:
                habits_list.append((habit_id, habit_name, streak))
                streak_emoji = "🔥" if streak >= 7 else "💪" if streak >= 3 else "👍"
                text += f"{streak_emoji} {habit_name} - {streak} дней подряд\n"
            
            text += f"\n💡 Продолжай в том же духе!"
            await message.answer(text, reply_markup=get_habits_menu(habits_list))

@router.message(F.text == "📰 Новости")
async def news_cmd(message: types.Message):
    await message.answer(
        "📰 <b>Умный агрегатор новостей</b>\n\n"
        "Этот модуль в разработке...\n\n"
        "Скоро здесь будет:\n"
        "• AI-саммари новостей\n"
        "• Персональные дайджесты\n"
        "• Ежедневные рассылки",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "🔮 Гороскоп")
async def horoscope_cmd(message: types.Message):
    await message.answer(
        "🔮 <b>Гороскоп</b>\n\n"
        "Этот модуль в разработке...\n\n"
        "Скоро здесь будет:\n"
        "• Ежедневные AI-гороскопы\n"
        "• Персональные предсказания\n"
        "• Совместимость знаков",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "💳 Подписки")
async def subscriptions_cmd(message: types.Message):
    await message.answer(
        "💳 <b>Менеджер подписок</b>\n\n"
        "Этот модуль в разработке...\n\n"
        "Скоро здесь будет:\n"
        "• Отслеживание подписок\n"
        "• Напоминания о платежах\n"
        "• Аналитика расходов",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "⚙️ Настройки")
async def settings_cmd(message: types.Message):
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Этот модуль в разработке...\n\n"
        "Скоро здесь будет:\n"
        "• Управление уведомлениями\n"
        "• Настройка времени рассылок",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "📈 Статистика")
async def stats_cmd(message: types.Message):
    async with get_async_session() as db:
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Сначала начните с команды /start")
            return
        
        stats_text = (
            f"📊 Твоя статистика:\n\n"
            f"🤖 AI-статистика:\n"
            f"🔹 Сегодня использовано: {user.daily_ai_requests}/5 запросов\n"
            f"🔹 Всего запросов: {user.total_ai_requests}"
        )
        
        await message.answer(stats_text, reply_markup=get_main_menu())

@router.message()
async def echo(message: types.Message):
    print(f"🔍 DEBUG: Получено сообщение: '{message.text}'")
    await message.answer(
        "😕 Я не понял эту команду\n\n"
        "Используй кнопки меню или введи /help для справки",
        reply_markup=get_main_menu()
    )

async def main():
    print("🤖 Milana_AI запускается...")
    
    # Автоматическая инициализация базы данных
    print("🔧 Проверка базы данных...")
    await init_db()
    print("✅ База данных готова!")
    
    bot = Bot(
        token=os.getenv('BOT_TOKEN'),
        default=DefaultBotProperties(parse_mode="HTML")
    )
    
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    print("🚀 Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
