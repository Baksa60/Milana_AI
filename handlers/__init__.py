# Feature flags для включения/выключения модулей
FEATURES = {
    "main": True,           # Всегда включен
    "habits": True,          # Полностью работает
    "horoscope": False,       # В разработке
    "subscriptions": False,    # В разработке  
    "news": False,           # В разработке
    "settings": False         # В разработке
}

from .main import router as main_router
from .habits import router as habits_router
from .horoscope import router as horoscope_router
from .subscriptions import router as subscriptions_router
from .news import router as news_router
from .settings import router as settings_router

def register_all_handlers(dp):
    """Регистрирует все обработчики в диспетчере"""
    # Основные команды всегда включены
    dp.include_router(main_router)
    
    # Включаем модули согласно feature flags
    if FEATURES.get("habits", False):
        dp.include_router(habits_router)
    if FEATURES.get("horoscope", False):
        dp.include_router(horoscope_router)
    if FEATURES.get("subscriptions", False):
        dp.include_router(subscriptions_router)
    if FEATURES.get("news", False):
        dp.include_router(news_router)
    if FEATURES.get("settings", False):
        dp.include_router(settings_router)
