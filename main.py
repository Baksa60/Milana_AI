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
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime, timedelta

from core.database import get_async_session, init_db
from models.user import User
from models.habit import Habit
from models.habit_log_new import HabitLog
from utils.keyboards import get_main_menu, get_habits_menu, get_habit_confirmation, get_habit_creation_confirmation, get_cancel_keyboard
from version import get_version, get_full_version

# Создаем роутер
router = Router()

class HabitStates(StatesGroup):
    adding_name = State()
    adding_description = State()
    adding_frequency = State()
    adding_goal = State()
    adding_target_days = State()
    adding_reminder_time = State()
    adding_color = State()
    confirming = State()

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
        f"🤖 <b>Версия:</b> Milana AI v{get_version()}\n"
        f"📊 <b>Трекер привычек:</b> v{get_version('habits')}\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Эта справка\n"
        "/version - Информация о версии\n\n"
        "💡 <b>Советы:</b>\n"
        "• Используй кнопки меню для навигации\n"
        "• AI-запросы ограничены: 5 в день бесплатно",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "/version")
async def version_cmd(message: types.Message):
    await message.answer(
        f"📋 <b>Информация о версии:</b>\n\n"
        f"{get_full_version()}",
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
            Habit.streak_current,
            Habit.last_completed_date
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
            for habit_id, habit_name, streak_current, last_completed_date in habits:
                habits_list.append((habit_id, habit_name, streak_current))
                
                # Проверяем выполнена ли привычка сегодня
                from datetime import date
                is_completed_today = last_completed_date == date.today()
                
                # Используем метод из модели для эмодзи стрика
                streak_emoji = "🔥" if streak_current >= 7 else "💪" if streak_current >= 3 else "👍"
                completed_mark = "✅" if is_completed_today else "⭕"
                text += f"{completed_mark} {streak_emoji} {habit_name} - {streak_current} дней подряд\n"
            
            text += f"\n💡 Продолжай в том же духе!"
            await message.answer(text, reply_markup=get_habits_menu(habits_list))

# Обработчики для добавления привычки
@router.message(F.text == "➕ Добавить привычку")
@router.callback_query(F.data == "habit_add")
async def add_habit_start(message_or_callback, state: FSMContext):
    """Начало процесса добавления привычки"""
    await state.set_state(HabitStates.adding_name)
    
    # Определяем тип объекта (message или callback)
    if hasattr(message_or_callback, 'message'):
        # Это callback query
        await message_or_callback.answer()
        await message_or_callback.message.answer(
            "📝 <b>Создание новой привычки</b>\n\n"
            "Шаг 1/5: Введи название привычки\n\n"
            "<i>Пример: 'Утренняя пробежка', 'Читать 30 минут', 'Медитация'</i>\n\n"
            "❌ Для отмены: /cancel",
            reply_markup=get_cancel_keyboard()
        )
    else:
        # Это message
        await message_or_callback.answer(
            "📝 <b>Создание новой привычки</b>\n\n"
            "Шаг 1/5: Введи название привычки\n\n"
            "<i>Пример: 'Утренняя пробежка', 'Читать 30 минут', 'Медитация'</i>\n\n"
            "❌ Для отмены: /cancel",
            reply_markup=get_cancel_keyboard()
        )

@router.message(HabitStates.adding_name)
async def add_habit_name(message: types.Message, state: FSMContext):
    """Обработка названия привычки"""
    name = message.text.strip()
    
    # Валидация
    if len(name) < 1:
        await message.answer("❌ Название не может быть пустым. Попробуй еще раз:")
        return
    
    if len(name) > 50:
        await message.answer("❌ Слишком длинное название (максимум 50 символов). Попробуй еще раз:")
        return
    
    # Сохраняем название и переходим к описанию
    await state.update_data(name=name)
    await state.set_state(HabitStates.adding_description)
    
    await message.answer(
        f"✅ Название: <b>{name}</b>\n\n"
        "Шаг 2/5: Введи описание (необязательно)\n\n"
        "<i>Зачем тебе эта привычка? Какую цель преследуешь?</i>\n\n"
        "❌ Для отмены: /cancel\n"
        "⏭️ Пропустить: /skip"
    )

@router.message(HabitStates.adding_description)
async def add_habit_description(message: types.Message, state: FSMContext):
    """Обработка описания привычки"""
    description = message.text.strip()
    
    # Валидация
    if len(description) > 500:
        await message.answer("❌ Слишком длинное описание (максимум 500 символов). Попробуй еще раз:")
        return
    
    # Сохраняем описание и переходим к частоте
    await state.update_data(description=description)
    await state.set_state(HabitStates.adding_frequency)
    
    await message.answer(
        f"📝 Описание: <b>{description}</b>\n\n"
        "Шаг 3/5: Выбери частоту выполнения\n\n"
        "🔄 <b>Варианты:</b>\n"
        "• <code>daily</code> - каждый день\n"
        "• <code>weekly</code> - каждую неделю\n"
        "• <code>custom</code> - свой график\n\n"
        "❌ Для отмены: /cancel"
    )

@router.message(HabitStates.adding_frequency)
async def add_habit_frequency(message: types.Message, state: FSMContext):
    """Обработка частоты привычки"""
    frequency = message.text.strip().lower()
    
    # Валидация
    valid_frequencies = ['daily', 'weekly', 'custom']
    if frequency not in valid_frequencies:
        await message.answer(
            "❌ Неверная частота. Выбери из:\n"
            "• <code>daily</code> - каждый день\n"
            "• <code>weekly</code> - каждую неделю\n"
            "• <code>custom</code> - свой график"
        )
        return
    
    # Сохраняем частоту и переходим к цели
    await state.update_data(frequency=frequency)
    await state.set_state(HabitStates.adding_goal)
    
    # Динамический текст в зависимости от частоты
    if frequency == 'daily':
        await message.answer(
            f"🔄 Частота: <b>каждый день</b>\n\n"
            "Шаг 4/5: Сколько раз в день нужно выполнить эту привычку?\n\n"
            "💡 <b>Примеры:</b>\n"
            "• <code>1</code> — один раз (например, медитация)\n"
            "• <code>3</code> — три раза (например, пить воду)\n"
            "• <code>8</code> — восемь раз (например, стаканы воды)\n\n"
            "❌ Для отмены: /cancel"
        )
    elif frequency == 'weekly':
        await message.answer(
            f"🔄 Частота: <b>каждую неделю</b>\n\n"
            "Шаг 4/5: Сколько раз в неделю ты хочешь это делать?\n\n"
            "💡 <b>Примеры:</b>\n"
            "• <code>3</code> — три раза (пн-ср-пт)\n"
            "• <code>5</code> — пять раз (только по будням)\n"
            "• <code>7</code> — семь раз (каждый день)\n\n"
            "❌ Для отмены: /cancel"
        )
    else:  # custom
        await message.answer(
            f"🔄 Частота: <b>по своему графику</b>\n\n"
            "Шаг 4/5: Сколько раз за период ты планируешь выполнять?\n\n"
            "💡 <b>Примеры:</b>\n"
            "• <code>2</code> — два раза за период\n"
            "• <code>5</code> — пять раз за период\n\n"
            "❌ Для отмены: /cancel"
        )

@router.message(HabitStates.adding_goal)
async def add_habit_goal(message: types.Message, state: FSMContext):
    """Обработка цели привычки"""
    goal_text = message.text.strip()
    
    # Валидация
    try:
        goal = int(goal_text)
        if goal <= 0 or goal > 50:
            await message.answer(
                "❌ <b>Некорректное значение!</b>\n\n"
                "Цель должна быть числом от 1 до 50.\n\n"
                "💡 <b>Примеры:</b>\n"
                "• <code>1</code> — один раз\n"
                "• <code>3</code> — три раза\n"
                "• <code>8</code> — восемь раз\n\n"
                "❌ Для отмены: /cancel",
                reply_markup=get_cancel_keyboard()
            )
            return
    except ValueError:
        await message.answer(
            "❌ <b>Нужно ввести число!</b>\n\n"
            "Цель должна быть числом от 1 до 50.\n\n"
            "💡 <b>Примеры:</b>\n"
            "• <code>1</code> — один раз\n"
            "• <code>3</code> — три раза\n"
            "• <code>8</code> — восемь раз\n\n"
            "❌ Для отмены: /cancel",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Сохраняем цель
    await state.update_data(goal=goal)
    await state.set_state(HabitStates.adding_target_days)
    
    await message.answer(
        f"🎯 <b>Цель установлена: {goal} раз</b>\n\n"
        "Шаг 5/6: На какой срок ты ставишь цель?\n\n"
        "💡 <b>Примеры:</b>\n"
        "• <code>30</code> — на месяц\n"
        "• <code>90</code> — на квартал\n"
        "• <code>365</code> — на год\n\n"
        "❌ Для отмены: /cancel",
        reply_markup=get_cancel_keyboard()
    )

@router.message(HabitStates.adding_target_days)
async def add_habit_target_days(message: types.Message, state: FSMContext):
    """Обработка срока привычки"""
    target_text = message.text.strip()
    
    # Валидация
    try:
        target_days = int(target_text)
        if target_days <= 0 or target_days > 3650:  # максимум 10 лет
            await message.answer(
                "❌ <b>Некорректное значение!</b>\n\n"
                "Срок должен быть числом от 1 до 3650 дней.\n\n"
                "💡 <b>Примеры:</b>\n"
                "• <code>30</code> — на месяц\n"
                "• <code>90</code> — на квартал\n"
                "• <code>365</code> — на год\n\n"
                "❌ Для отмены: /cancel",
                reply_markup=get_cancel_keyboard()
            )
            return
    except ValueError:
        await message.answer(
            "❌ <b>Нужно ввести число!</b>\n\n"
            "Срок должен быть числом от 1 до 3650 дней.\n\n"
            "💡 <b>Примеры:</b>\n"
            "• <code>30</code> — на месяц\n"
            "• <code>90</code> — на квартал\n"
            "• <code>365</code> — на год\n\n"
            "❌ Для отмены: /cancel",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Сохраняем срок
    await state.update_data(target_days=target_days)
    await state.set_state(HabitStates.confirming)
    
    # Показываем подтверждение
    data = await state.get_data()
    await message.answer(
        f"📝 <b>Проверь данные привычки:</b>\n\n"
        f"🏷️ <b>Название:</b> {data['name']}\n"
        f"📝 <b>Описание:</b> {data['description']}\n"
        f"🔄 <b>Частота:</b> {data['frequency']}\n"
        f"🎯 <b>Цель:</b> {data['goal']} раз в период\n"
        f"📅 <b>Срок:</b> {data['target_days']} дней\n\n"
        f"Все верно?",
        reply_markup=get_habit_creation_confirmation()
    )

@router.callback_query(F.data == "confirm_habit")
async def confirm_habit(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение создания привычки"""
    data = await state.get_data()
    
    async with get_async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        # Создаем привычку
        habit = Habit(
            user_id=user.id,
            name=data['name'],
            description=data.get('description'),
            frequency=data['frequency'],
            goal=data['goal'],
            target_days=data['target_days'],
            created_at=date.today()
        )
        
        db.add(habit)
        await db.commit()
        
        await callback.answer("✅ Привычка создана!")
        await callback.message.answer(
            f"🎉 <b>Привычка создана!</b>\n\n"
            f"🏷️ {data['name']}\n"
            f"🎯 Цель: {data['goal']} раз в период на {data['target_days']} дней\n\n"
            f"💡 Не забывай отмечать выполнение каждый день!",
            reply_markup=get_main_menu()
        )
    
    await state.clear()

@router.callback_query(F.data.startswith("habit_complete_"))
async def complete_habit(callback: types.CallbackQuery, state: FSMContext):
    """Отметка выполнения привычки"""
    habit_id = int(callback.data.split("_")[2])
    await callback.answer()
    
    async with get_async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.message.answer("❌ Пользователь не найден")
            return
        
        # Получаем привычку
        habit = await db.get(Habit, habit_id)
        if not habit or habit.user_id != user.id:
            await callback.message.answer("❌ Привычка не найдена")
            return
        
        from datetime import date
        today = date.today()
        
        # Проверяем, не выполнена ли уже сегодня
        if habit.last_completed_date == today:
            await callback.message.answer(
                f"✅ <b>Привычка уже выполнена сегодня!</b>\n\n"
                f"🏷️ {habit.name}\n"
                f"🔥 Стрик: {habit.streak_current} дней\n\n"
                f"💡 Отличная работа! Завтра продолжим!",
                reply_markup=get_main_menu()
            )
            return
        
        # Обновляем стрик
        if habit.last_completed_date == today - timedelta(days=1):
            # Вчера было выполнено - увеличиваем стрик
            habit.streak_current += 1
        else:
            # Пропуск - сбрасываем стрик
            habit.streak_current = 1
        
        # Обновляем дату выполнения
        habit.last_completed_date = today
        
        # Добавляем запись в лог
        habit_log = HabitLog(
            habit_id=habit.id,
            user_id=user.id,
            completed_at=datetime.now(),
            date=today
        )
        
        db.add(habit_log)
        await db.commit()
        
        # Начисляем XP пользователю
        user.xp += 10
        await db.commit()
        
        # Определяем уровень
        if user.xp >= 500:
            level = "👑 Мастер"
        elif user.xp >= 100:
            level = "💪 Профи"
        else:
            level = "🌱 Новичок"
        
        await callback.message.answer(
            f"🎉 <b>Привычка выполнена!</b>\n\n"
            f"🏷️ {habit.name}\n"
            f"🔥 Стрик: {habit.streak_current} дней подряд\n"
            f"💰 +10 XP earned!\n"
            f"🎯 Твой уровень: {level}\n\n"
            f"💡 Отличная работа! Продолжай в том же духе!",
            reply_markup=get_main_menu()
        )

@router.callback_query(F.data == "habit_delete")
async def delete_habit_start(callback: types.CallbackQuery, state: FSMContext):
    """Начало процесса удаления привычки"""
    await callback.answer()
    
    async with get_async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.message.answer("❌ Пользователь не найден")
            return
        
        # Получаем активные привычки
        query = select(
            Habit.id, 
            Habit.name, 
            Habit.streak_current
        ).where(
            and_(Habit.user_id == user.id, Habit.is_active == True)
        ).order_by(Habit.created_at)
        
        result = await db.execute(query)
        habits = result.all()
        
        if not habits:
            await callback.message.answer(
                "📊 У тебя пока нет привычек для удаления",
                reply_markup=get_main_menu()
            )
            return
        
        # Создаем клавиатуру с привычками для удаления
        builder = InlineKeyboardBuilder()
        for habit_id, habit_name, streak in habits:
            builder.row(
                InlineKeyboardButton(
                    text=f"🗑️ {habit_name} ({streak} дней)",
                    callback_data=f"delete_habit_{habit_id}"
                )
            )
        
        builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
        
        await callback.message.answer(
            "🗑️ <b>Удаление привычки</b>\n\n"
            "Выбери привычку для удаления:",
            reply_markup=builder.as_markup()
        )

@router.callback_query(F.data.startswith("delete_habit_"))
async def delete_habit_confirm(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение удаления привычки"""
    habit_id = int(callback.data.split("_")[2])
    await callback.answer()
    
    async with get_async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.message.answer("❌ Пользователь не найден")
            return
        
        # Получаем информацию о привычке
        habit = await db.get(Habit, habit_id)
        if not habit or habit.user_id != user.id:
            await callback.message.answer("❌ Привычка не найдена")
            return
        
        # Создаем клавиатуру подтверждения
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="🗑️ Удалить",
                callback_data=f"confirm_delete_{habit_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel"
            )
        )
        
        await callback.message.answer(
            f"⚠️ <b>Точно удалить привычку?</b>\n\n"
            f"🏷️ <b>{habit.name}</b>\n"
            f"� <b>Стрик: {habit.streak_current} дней</b>\n\n"
            f"❗️ <i>Это действие нельзя отменить!</i>",
            reply_markup=builder.as_markup()
        )

@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_habit_execute(callback: types.CallbackQuery, state: FSMContext):
    """Выполнение удаления привычки"""
    habit_id = int(callback.data.split("_")[2])
    await callback.answer()
    
    async with get_async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.message.answer("❌ Пользователь не найден")
            return
        
        # Получаем привычку
        habit = await db.get(Habit, habit_id)
        if not habit or habit.user_id != user.id:
            await callback.message.answer("❌ Привычка не найдена")
            return
        
        habit_name = habit.name
        
        # Жесткое удаление из БД
        await db.delete(habit)
        await db.commit()
        
        await callback.message.answer(
            f"🗑️ <b>Привычка удалена навсегда</b>\n\n"
            f"🏷️ {habit_name}\n\n"
            f"💡 Ты всегда можешь создать новую привычку с тем же названием",
            reply_markup=get_main_menu()
        )

@router.callback_query(F.data == "cancel_habit")
async def cancel_habit(callback: types.CallbackQuery, state: FSMContext):
    """Отмена создания привычки"""
    await state.clear()
    await callback.answer("❌ Создание отменено")
    await callback.message.answer(
        "🚫 Создание привычки отменено\n\n"
        "Возвращаю в главное меню...",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    """Универсальная отмена действия"""
    current_state = await state.get_state()
    
    if current_state:
        await state.clear()
        await callback.answer("❌ Действие отменено")
        await callback.message.answer(
            "🚫 Действие отменено\n\n"
            "Возвращаю в главное меню...",
            reply_markup=get_main_menu()
        )
    else:
        await callback.answer()
        await callback.message.answer(
            "🚫 Отмена\n\n"
            "Возвращаю в главное меню...",
            reply_markup=get_main_menu()
        )
@router.message(F.text == "/cancel")
async def cancel_cmd(message: types.Message, state: FSMContext):
    """Отмена текущего действия"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("ℹ️ Нет активных действий")
        return
    
    await state.clear()
    await message.answer(
        "🚫 Действие отменено\n\n"
        "Возвращаю в главное меню...",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "/skip")
async def skip_cmd(message: types.Message, state: FSMContext):
    """Пропуск текущего шага"""
    current_state = await state.get_state()
    
    if current_state == HabitStates.adding_description.state:
        await state.update_data(description="")
        await state.set_state(HabitStates.adding_frequency)
        await message.answer(
            "⏭️ Описание пропущено\n\n"
            "Шаг 3/5: Выбери частоту выполнения\n\n"
            "🔄 <b>Варианты:</b>\n"
            "• <code>daily</code> - каждый день\n"
            "• <code>weekly</code> - каждую неделю\n"
            "• <code>custom</code> - свой график\n\n"
            "❌ Для отмены: /cancel"
        )
    else:
        await message.answer("ℹ️ Пропуск недоступен на этом шаге")

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
    print(f"🤖 Milana AI v{get_version()} запускается...")
    
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
    
    try:
        print(f"🚀 Milana AI v{get_version()} запущен и готов к работе!")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n🛑 Бот останавливается...")
        await bot.session.close()
        print("✅ Бот корректно остановлен")

if __name__ == "__main__":
    asyncio.run(main())
