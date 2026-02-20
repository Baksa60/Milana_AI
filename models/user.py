from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

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
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи с другими моделями
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"
