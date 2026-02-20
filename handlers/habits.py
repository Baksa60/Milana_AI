from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime

from core.database import get_async_session
from models.user import User
from models.habit import Habit, HabitRecord
from utils.keyboards import get_habits_menu, get_habit_confirmation, get_cancel_keyboard, get_main_menu

router = Router(name="habits")

class HabitStates(StatesGroup):
    adding_name = State()
    deleting = State()

async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    """Вспомогательная функция для поиска пользователя по telegram_id"""
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()

@router.message(F.text == "📊 Трекер привычек")
async def show_habits_menu(message: types.Message):
    """Показать меню трекера привычек"""
    async with get_async_session() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
        if not user:
            await message.answer("❌ Сначала начните с команды /start")
            return
        
        # Получаем активные привычки пользователя
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
                # Добавляем эмодзи для стрика
                streak_emoji = "🔥" if streak >= 7 else "💪" if streak >= 3 else "👍"
                text += f"{streak_emoji} {habit_name} - {streak} дней подряд\n"
            
            text += f"\n💡 Продолжай в том же духе!"
            
            await message.answer(text, reply_markup=get_habits_menu(habits_list))

@router.callback_query(F.data == "habit_add")
async def start_adding_habit(callback: types.CallbackQuery, state: FSMContext):
    """Начать добавление новой привычки"""
    await callback.message.edit_text(
        "➕ <b>Новая привычка</b>\n\n"
        "Напиши название привычки (например: 'Пить воду', 'Читать 30 минут')",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(HabitStates.adding_name)

@router.message(HabitStates.adding_name)
async def process_habit_name(message: types.Message, state: FSMContext):
    """Обработать название привычки"""
    habit_name = message.text.strip()
    
    if len(habit_name) < 2:
        await message.answer("❌ Название слишком короткое. Попробуйте еще раз:")
        return
    
    if len(habit_name) > 200:
        await message.answer("❌ Название слишком длинное. Максимум 200 символов:")
        return
    
    async with get_async_session() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
        
        # Проверяем, нет ли уже такой привычки
        existing_query = select(Habit).where(
            and_(
                Habit.user_id == user.id,
                Habit.name == habit_name,
                Habit.is_active == True
            )
        )
        existing_habit = await db.scalar(existing_query)
        
        if existing_habit:
            await message.answer(
                f"❌ Привычка '{habit_name}' уже существует\n\n"
                "Попробуйте другое название:",
                reply_markup=get_cancel_keyboard()
            )
            return
        
        # Создаем новую привычку
        new_habit = Habit(
            user_id=user.id,
            name=habit_name,
            target_days=30  # Цель по умолчанию
        )
        db.add(new_habit)
        await db.commit()
        
        await message.answer(
            f"✅ Привычка '{habit_name}' добавлена!\n\n"
            f"🎯 Цель: {new_habit.target_days} дней подряд\n"
            f"🔥 Текущий стрик: 0 дней\n\n"
            "Теперь каждый день отмечай выполнение!",
            reply_markup=get_main_menu()
        )
        
        await state.clear()

@router.callback_query(F.data.startswith("habit_complete_"))
async def show_habit_confirmation(callback: types.CallbackQuery):
    """Показать подтверждение выполнения привычки"""
    habit_id = int(callback.data.split("_")[-1])
    
    async with get_async_session() as db:
        habit = await db.get(Habit, habit_id)
        if not habit:
            await callback.answer("❌ Привычка не найдена", show_alert=True)
            return
        
        # Проверяем, не отмечали ли уже сегодня
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        
        existing_record_query = select(HabitRecord).where(
            and_(
                HabitRecord.habit_id == habit_id,
                HabitRecord.completed_at >= today_start
            )
        )
        existing_record = await db.scalar(existing_record_query)
        
        if existing_record:
            await callback.answer("✅ Сегодня уже отмечено!", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"🎯 <b>{habit.name}</b>\n\n"
            f"Текущий стрик: {habit.current_streak} дней 🔥\n\n"
            "Ты действительно выполнил(а) эту привычку сегодня?",
            reply_markup=get_habit_confirmation(habit_id, habit.name)
        )

@router.callback_query(F.data.startswith("habit_confirm_"))
async def confirm_habit_completion(callback: types.CallbackQuery):
    """Подтвердить выполнение привычки"""
    habit_id = int(callback.data.split("_")[-1])
    
    async with get_async_session() as db:
        habit = await db.get(Habit, habit_id)
        if not habit:
            await callback.answer("❌ Привычка не найдена", show_alert=True)
            return
        
        # Создаем запись о выполнении
        record = HabitRecord(habit_id=habit_id)
        db.add(record)
        
        # Обновляем стрик
        habit.current_streak += 1
        
        # Обновляем лучший стрик
        if habit.current_streak > habit.best_streak:
            habit.best_streak = habit.current_streak
        
        await db.commit()
        
        # Определяем сообщение в зависимости от стрика
        streak_messages = {
            1: "Отличное начало! 👍",
            3: "Три дня подряд! 💪",
            7: "Неделя! Ты на верном пути! 🔥",
            14: "Две недели! Это впечатляет! 🌟",
            30: "Месяц! Ты сформировал(а) привычку! 🎉"
        }
        
        congrats = streak_messages.get(habit.current_streak, "Так держать! 💪")
        
        await callback.message.edit_text(
            f"✅ <b>{habit.name}</b> выполнена!\n\n"
            f"🔥 Стрик: {habit.current_streak} дней\n"
            f"🏆 Лучший стрик: {habit.best_streak} дней\n\n"
            f"{congrats}",
            reply_markup=get_main_menu()
        )

@router.callback_query(F.data == "habit_delete")
async def start_deleting_habit(callback: types.CallbackQuery, state: FSMContext):
    """Начать удаление привычки"""
    async with get_async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        
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
            await callback.answer("❌ Нет привычек для удаления", show_alert=True)
            return
        
        text = "🗑️ <b>Удаление привычки</b>\n\n"
        keyboard_buttons = []
        
        for habit_id, habit_name, streak in habits:
            text += f"• {habit_name} ({streak} дней)\n"
            keyboard_buttons.append(
                types.InlineKeyboardButton(
                    text=f"🗑️ {habit_name}",
                    callback_data=f"delete_habit_{habit_id}"
                )
            )
        
        text += "\nВыбери привычку для удаления:"
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            keyboard_buttons[i:i+2] for i in range(0, len(keyboard_buttons), 2)
        ])
        keyboard.row(types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
        
        await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("delete_habit_"))
async def delete_habit(callback: types.CallbackQuery):
    """Удалить привычку"""
    habit_id = int(callback.data.split("_")[-1])
    
    async with get_async_session() as db:
        habit = await db.get(Habit, habit_id)
        if not habit:
            await callback.answer("❌ Привычка не найдена", show_alert=True)
            return
        
        habit_name = habit.name
        
        # Мягкое удаление (деактивация)
        habit.is_active = False
        await db.commit()
        
        await callback.message.edit_text(
            f"🗑️ Привычка '{habit_name}' удалена\n\n"
            "Все записи сохранены в статистике.",
            reply_markup=get_main_menu()
        )

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    """Отменить текущее действие"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Действие отменено\n\n"
        "Возвращаю в главное меню:",
        reply_markup=get_main_menu()
    )
