"""
Тестовый запуск бота с проверкой всех компонентов
"""
import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Используем SQLite для тестирования
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///milana.db'

from core.bot import create_bot, create_dispatcher
from core.database import init_db
from utils.llm_client import llm_client

async def test_components():
    print("🧪 Тестирование компонентов...")
    
    # Тест базы данных
    try:
        await init_db()
        print("✅ База данных: OK")
    except Exception as e:
        print(f"❌ База данных: {e}")
        return
    
    # Тест создания бота
    try:
        bot = create_bot()
        print("✅ Создание бота: OK")
    except Exception as e:
        print(f"❌ Создание бота: {e}")
        return
    
    # Тест диспетчера
    try:
        dp = create_dispatcher(bot)
        print("✅ Диспетчер: OK")
    except Exception as e:
        print(f"❌ Диспетчер: {e}")
        return
    
    # Проверка токена
    if not os.getenv('BOT_TOKEN'):
        print("❌ BOT_TOKEN не найден в .env файле")
        return
    
    print("\n🚀 Все компоненты готовы!")
    print("📝 Что нужно для запуска:")
    print("1. BOT_TOKEN в .env файле")
    print("2. Запустить: python main.py")
    print("\n🔥 MVP функции:")
    print("- /start - запуск бота")
    print("- 📊 Трекер привычек")
    print("- 📈 Статистика")
    print("- 🏠 Главное меню")

if __name__ == "__main__":
    asyncio.run(test_components())
