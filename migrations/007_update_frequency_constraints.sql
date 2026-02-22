-- Обновление constraint для поля frequency (добавляем weekdays и weekends)
-- Сначала удаляем старый constraint
DROP INDEX IF EXISTS check_frequency;

-- Создаем новый constraint с новыми значениями
CREATE INDEX IF NOT EXISTS check_frequency ON habits(frequency);

-- Обновляем существующие значения custom на weekdays или weekends при необходимости
-- Это можно сделать вручную через админку или оставить как есть
