"""
Скрипт для выполнения миграций БД
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///data/milana.db'

from sqlalchemy import text
from core.database import engine, get_async_session

async def run_migration(migration_file: str):
    """Выполнить миграцию из SQL файла"""
    print(f"🔄 Выполнение миграции: {migration_file}")
    
    # Читаем SQL файл
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Разделяем на отдельные команды
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    # Выполняем каждую команду отдельно
    async with engine.begin() as conn:
        for statement in statements:
            if statement:
                await conn.execute(text(statement))
    
    print(f"✅ Миграция {migration_file} выполнена успешно")

async def check_migration_table():
    """Проверить и создать таблицу миграций"""
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

async def is_migration_applied(filename: str) -> bool:
    """Проверить применена ли миграция"""
    async with get_async_session() as session:
        result = await session.execute(
            text("SELECT COUNT(*) FROM schema_migrations WHERE filename = :filename"),
            {"filename": filename}
        )
        count = result.scalar()
        return count > 0

async def mark_migration_applied(filename: str):
    """Отметить миграцию как примененную"""
    async with get_async_session() as session:
        await session.execute(
            text("INSERT INTO schema_migrations (filename) VALUES (:filename)"),
            {"filename": filename}
        )
        await session.commit()

async def run_all_migrations():
    """Выполнить все непримененные миграции"""
    print("🔧 Проверка миграций...")
    
    # Создаем таблицу миграций
    await check_migration_table()
    
    # Список миграций в порядке выполнения
    MIGRATIONS = [
        "001_create_habits_tables.sql",
        "002_update_habits_structure.sql", 
        "003_update_users_table.sql",
        "004_add_user_id_to_habit_logs.sql",
        "005_add_target_days_to_habits.sql",
        "006_add_last_completed_date_to_habits.sql",
        "007_update_frequency_constraints.sql"
    ]
    
    applied_count = 0
    
    for migration_file in MIGRATIONS:
        filename = os.path.basename(migration_file)
        
        if await is_migration_applied(filename):
            print(f"⏭️  Миграция {filename} уже применена")
            continue
        
        # Выполняем миграцию
        migration_path = os.path.join("migrations", migration_file)
        await run_migration(migration_path)
        
        # Отмечаем как примененную
        await mark_migration_applied(filename)
        applied_count += 1
    
    print(f"🎉 Применено миграций: {applied_count}")

if __name__ == "__main__":
    asyncio.run(run_all_migrations())
