-- Проверяем существование колонки перед добавлением
-- ALTER TABLE habits ADD COLUMN last_completed_date DATE;

-- Создание индекса для last_completed_date (если еще не создан)
CREATE INDEX IF NOT EXISTS idx_habits_last_completed_date ON habits(last_completed_date);
