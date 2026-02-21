from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    timezone = Column(String(50), default="UTC")  # Часовой пояс пользователя
    notifications_enabled = Column(Boolean, default=True)
    
    # AI лимиты и статистика
    daily_ai_requests = Column(Integer, default=0)
    total_ai_requests = Column(Integer, default=0)
    last_ai_request_date = Column(Date, nullable=True)
    
    # Настройки уведомлений
    notification_time = Column(Time, default=func.time('09:00:00'))  # Время для ежедневных уведомлений
    
    # Геймификация для трекера привычек
    xp = Column(Integer, default=0, comment="Опыт пользователя")
    level = Column(Integer, default=1, comment="Уровень пользователя")
    total_habits_completed = Column(Integer, default=0, comment="Всего привычек выполнено")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Убираем relationship чтобы избежать циклического импорта
    # habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    # subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"
    
    @property
    def level_emoji(self) -> str:
        """Эмодзи для уровня"""
        if self.level >= 10:
            return "👑"
        elif self.level >= 5:
            return "🏆"
        elif self.level >= 3:
            return "🥇"
        else:
            return "🌟"
    
    def add_xp(self, amount: int) -> bool:
        """Добавить опыт, проверить повышение уровня"""
        self.xp += amount
        self.total_habits_completed += 1
        
        # Проверка повышения уровня (простая формула: 100 XP за уровень)
        new_level = min(self.xp // 100 + 1, 50)  # макс 50 уровень
        leveled_up = new_level > self.level
        self.level = new_level
        
        return leveled_up
    
    def get_xp_to_next_level(self) -> int:
        """XP до следующего уровня"""
        if self.level >= 50:
            return 0
        return (self.level * 100) - self.xp
