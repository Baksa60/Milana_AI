"""
Скрипт для быстрой настройки базы данных SQLite для тестирования
"""
import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Изменяем DATABASE_URL на SQLite для тестирования
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///milana.db'

from core.database import init_db

async def main():
    print("🔧 Создание базы данных...")
    await init_db()
    print("✅ База данных готова!")

if __name__ == "__main__":
    asyncio.run(main())
