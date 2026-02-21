from sqlalchemy.ext.declarative import declarative_base

# Единая Base для всех моделей
Base = declarative_base()

from .user import User
from .habit import Habit
from .habit_log_new import HabitLog
from .subscription import Subscription
from .horoscope import HoroscopeCache
from .news import NewsDigest, NewsSource

__all__ = [
    "Base",
    "User",
    "Habit", 
    "HabitLog",
    "Subscription",
    "HoroscopeCache",
    "NewsDigest",
    "NewsSource"
]
