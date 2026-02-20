-- Миграция 003: Обновление таблицы users для геймификации
-- Дата: 2026-02-20
-- Автор: Игорь Максимов + Cascade AI

-- Добавляем поля для геймификации в таблицу users
ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1;
ALTER TABLE users ADD COLUMN total_habits_completed INTEGER DEFAULT 0;

-- Создаем индексы для производительности
CREATE INDEX IF NOT EXISTS idx_users_level ON users(level);
CREATE INDEX IF NOT EXISTS idx_users_xp ON users(xp);
