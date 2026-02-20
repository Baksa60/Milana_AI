# 🔄 Гайд по миграции в modules/

Этот документ описывает, как мигрировать с текущей структуры `handlers/` в модульную архитектуру `modules/`.

## 📁 Текущая структура
```
Milana_AI/
├── handlers/
│   ├── main.py        # router = Router()
│   ├── habits.py      # router = Router(name="habits")
│   ├── horoscope.py   # router = Router(name="horoscope")
│   ├── subscriptions.py
│   ├── news.py
│   └── settings.py
└── models/
    ├── user.py
    ├── habit.py
    └── ...
```

## 🎯 Целевая структура
```
Milana_AI/
├── core/              # Ядро бота
├── utils/             # Общие утилиты
├── models/            # Общие модели
└── modules/
    ├── habits/
    │   ├── handlers.py    # ← из handlers/habits.py
    │   ├── models.py      # ← из models/habit.py
    │   └── services.py    # ← новая бизнес-логика
    ├── horoscope/
    │   ├── handlers.py    # ← из handlers/horoscope.py
    │   └── services.py
    └── subscriptions/
        ├── handlers.py    # ← из handlers/subscriptions.py
        ├── models.py      # ← из models/subscription.py
        └── services.py
```

## 🚀 Пошаговая миграция

### Шаг 1: Подготовка
```bash
# Создаем структуру modules/
mkdir modules
mkdir modules/habits
mkdir modules/horoscope
mkdir modules/subscriptions
mkdir modules/news
mkdir modules/settings
```

### Шаг 2: Миграция handlers
```bash
# Переносим файлы handlers
mv handlers/habits.py modules/habits/handlers.py
mv handlers/horoscope.py modules/horoscope/handlers.py
mv handlers/subscriptions.py modules/subscriptions/handlers.py
mv handlers/news.py modules/news/handlers.py
mv handlers/settings.py modules/settings/handlers.py
```

### Шаг 3: Миграция models
```bash
# Переносим модели
mv models/habit.py modules/habits/models.py
mv models/horoscope.py modules/horoscope/models.py
mv models/subscription.py modules/subscriptions/models.py
mv models/news.py modules/news/models.py
```

### Шаг 4: Обновление импортов
```python
# Было в modules/habits/handlers.py
from models.user import User
from models.habit import Habit

# Стало в modules/habits/handlers.py
from models.user import User
from .models import Habit
```

### Шаг 5: Обновление регистрации
```python
# Было в handlers/__init__.py
from .habits import router as habits_router

# Стало в main.py
from modules.habits.handlers import router as habits_router
from modules.horoscope.handlers import router as horoscope_router

async def main():
    dp = create_dispatcher(bot)
    dp.include_router(habits_router)
    dp.include_router(horoscope_router)
```

## 🎯 Преимущества миграции

1. **Изоляция фич** - каждая фича в своей папке
2. **Легкое удаление** - просто удалить папку modules/feature
3. **Командная работа** - разные разработчики на разных модулях
4. **Микросервисы** - легко выделить в отдельный сервис

## ⚠️ Что нужно учесть

1. **Импорты моделей** - обновить относительные импорты
2. **Имена роутеров** - убрать `name="habits"` после миграции
3. **Feature flags** - перенести в main.py
4. **Тесты** - обновить пути к тестам

## 🔄 Автоматизация миграции

Можно создать скрипт для автоматической миграции:
```python
# migrate_to_modules.py
import os
import shutil

def migrate_module(module_name):
    """Мигрирует один модуль"""
    # Создаем папку
    os.makedirs(f"modules/{module_name}", exist_ok=True)
    
    # Переносим handlers
    shutil.move(f"handlers/{module_name}.py", f"modules/{module_name}/handlers.py")
    
    # Переносим models если есть
    if os.path.exists(f"models/{module_name}.py"):
        shutil.move(f"models/{module_name}.py", f"modules/{module_name}/models.py")

# Запуск миграции
for module in ["habits", "horoscope", "subscriptions", "news", "settings"]:
    migrate_module(module)
```

## 🎉 Результат

После миграции получим:
- ✅ Чистую модульную архитектуру
- ✅ Изолированные фичи
- ✅ Легкое масштабирование
- ✅ Подготовку к микросервисам

---

**💡 Совет:** Мигрируйте по одному модулю за раз, чтобы ничего не сломать!
