import asyncio
import logging
import os
from dotenv import load_dotenv

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Используем SQLite для стабильности
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///milana.db'

from aiogram import Dispatcher, Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from core.database import init_db
from handlers import register_all_handlers

async def main():
    logger.info("🚀 Запуск Milana AI Bot...")
    
    # Проверяем переменные окружения
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("❌ BOT_TOKEN не найден в переменных окружения")
        return
    
    if len(bot_token) < 20:
        logger.error(f"❌ BOT_TOKEN слишком короткий: {len(bot_token)} символов")
        return
    
    logger.info(f"✅ BOT_TOKEN найден, длина: {len(bot_token)} символов")
    
    try:
        # Создаем бота
        logger.info("🤖 Создание бота...")
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Проверяем валидность токена
        logger.info("🔍 Проверка валидности токена...")
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот найден: @{bot_info.username} ({bot_info.first_name})")
        
        # Создаем диспетчер
        logger.info("📋 Создание диспетчера...")
        dp = Dispatcher(bot=bot)
        
        # Регистрируем обработчики
        logger.info("🔧 Регистрация обработчиков...")
        register_all_handlers(dp)
        logger.info("✅ Обработчики зарегистрированы")
        
        # Инициализируем базу данных
        logger.info("💾 Инициализация базы данных...")
        await init_db()
        logger.info("✅ База данных готова")
        
        # Запускаем бота
        logger.info("🚀 Запуск поллинга...")
        await dp.start_polling(
            bot,
            handle_signals=False,
            on_startup=lambda *args: logger.info("🎉 Бот успешно запущен!"),
            on_shutdown=lambda *args: logger.info("🛑 Бот остановлен")
        )
        
    except TelegramAPIError as e:
        logger.error(f"❌ Ошибка Telegram API: {e}")
        if "Unauthorized" in str(e):
            logger.error("💡 Токен невалидный. Проверьте BOT_TOKEN в .env файле")
        elif "Conflict" in str(e):
            logger.error("💡 Конфликт токена. Возможно, бот уже запущен в другом процессе")
    except Exception as e:
        logger.error(f"❌ Неизвестная ошибка: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
