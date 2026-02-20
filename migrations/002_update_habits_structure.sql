-- Миграция 002: Обновление структуры таблицы habits
-- Дата: 2026-02-20
-- Автор: Игорь Максимов + Cascade AI

-- Добавляем новые поля в существующую таблицу habits
ALTER TABLE habits ADD COLUMN frequency VARCHAR(20) DEFAULT 'daily';
ALTER TABLE habits ADD COLUMN goal INTEGER DEFAULT 1;
ALTER TABLE habits ADD COLUMN streak_current INTEGER DEFAULT 0;
ALTER TABLE habits ADD COLUMN last_completed_date DATE;
ALTER TABLE habits ADD COLUMN reminder_time TIME;
ALTER TABLE habits ADD COLUMN color VARCHAR(20) DEFAULT 'blue';

-- Переименовываем старые поля для совместимости
-- Если старые поля существуют, переносим данные в новые
UPDATE habits SET frequency = 'daily' WHERE frequency IS NULL;
UPDATE habits SET goal = 1 WHERE goal IS NULL;
UPDATE habits SET streak_current = current_streak WHERE streak_current IS NULL AND current_streak IS NOT NULL;
UPDATE habits SET last_completed_date = created_at WHERE last_completed_date IS NULL AND created_at IS NOT NULL;

-- Удаляем старые поля если они существуют
-- Note: SQLite не поддерживает DROP COLUMN напрямую, поэтому пересоздаем таблицу

-- Создаем новую временную таблицу
CREATE TABLE habits_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    frequency VARCHAR(20) DEFAULT 'daily' CHECK (frequency IN ('daily', 'weekly', 'custom')),
    goal INTEGER DEFAULT 1 CHECK (goal > 0 AND goal <= 50),
    streak_current INTEGER DEFAULT 0,
    last_completed_date DATE,
    reminder_time TIME,
    color VARCHAR(20) DEFAULT 'blue' CHECK (color IN ('blue', 'green', 'red', 'yellow', 'purple', 'orange')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

-- Копируем данные из старой таблицы
INSERT INTO habits_new (
    id, user_id, name, description, is_active, 
    frequency, goal, streak_current, last_completed_date, 
    reminder_time, color, created_at, updated_at
)
SELECT 
    id, user_id, name, description, is_active,
    frequency, goal, streak_current, last_completed_date,
    reminder_time, color, created_at, updated_at
FROM habits;

-- Удаляем старую таблицу
DROP TABLE habits;

-- Переименовываем новую таблицу
ALTER TABLE habits_new RENAME TO habits;

-- Создаем индексы
CREATE INDEX IF NOT EXISTS idx_habits_user_id ON habits(user_id);
CREATE INDEX IF NOT EXISTS idx_habits_active ON habits(is_active);
