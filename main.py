from aiogram import Dispatcher, Bot
from core.bot import create_bot, create_dispatcher
from core.database import init_db
import asyncio

async def main():
    bot = create_bot()
    dp = create_dispatcher(bot)
    await init_db()
    print("🤖 Milana_AI запущена...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
