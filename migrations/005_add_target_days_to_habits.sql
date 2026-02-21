-- Добавление target_days в habits
ALTER TABLE habits ADD COLUMN target_days INTEGER DEFAULT 30;

-- Создание индекса для target_days
CREATE INDEX idx_habits_target_days ON habits(target_days);
