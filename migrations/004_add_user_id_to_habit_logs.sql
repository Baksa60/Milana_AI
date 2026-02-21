-- Добавление user_id в habit_logs
ALTER TABLE habit_logs ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;

-- Создание индекса для user_id
CREATE INDEX idx_habit_logs_user_id ON habit_logs(user_id);

-- Создание внешнего ключа
CREATE INDEX idx_habit_logs_user_id_fk ON habit_logs(user_id);
