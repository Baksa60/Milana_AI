from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from config import get_settings
from handlers import register_all_handlers

def create_bot() -> Bot:
    settings = get_settings()
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

def create_dispatcher(bot: Bot) -> Dispatcher:
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)
    
    # Регистрируем все обработчики
    register_all_handlers(dp)
    
    return dp
