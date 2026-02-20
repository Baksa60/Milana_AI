from .main import router as main_router
from .habits import router as habits_router
from .horoscope import router as horoscope_router
from .subscriptions import router as subscriptions_router
from .news import router as news_router
from .settings import router as settings_router

def register_all_handlers(dp):
    """Регистрирует все обработчики в диспетчере"""
    dp.include_router(main_router)
    dp.include_router(habits_router)
    dp.include_router(horoscope_router)
    dp.include_router(subscriptions_router)
    dp.include_router(news_router)
    dp.include_router(settings_router)
