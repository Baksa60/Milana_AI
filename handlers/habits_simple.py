from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

router = Router()

class HabitStates(StatesGroup):
    adding_name = State()

@router.message()
async def test_handler(message):
    await message.answer("Test")
