"""
Модель привычек для трекера
"""
from datetime import date, time
from sqlalchemy import Column, Integer, String, Boolean, Text, Date, Time, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from core.database import Base

class Habit(Base):
    """Модель привычек"""
    __tablename__ = "habits"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    
    # Описание привычки
    name = Column(String(50), nullable=False, comment="Название привычки")
    description = Column(Text, comment="Описание/цель привычки")
    
    # Настройки частоты и цели
    frequency = Column(
        String(20), 
        default="daily",
        comment="Частота: daily, weekly, custom"
    )
    goal = Column(
        Integer, 
        default=1,
        comment="Цель: сколько раз в период"
    )
    
    # Геймификация
    streak_current = Column(Integer, default=0, comment="Текущий стрик")
    last_completed_date = Column(Date, comment="Дата последнего выполнения")
    
    # Визуализация и напоминания
    color = Column(String(20), default="blue", comment="Цвет для визуализации")
    reminder_time = Column(Time, comment="Время напоминания")
    
    # Статус
    is_active = Column(Boolean, default=True, comment="Активна ли привычка")
    
    # Метаданные
    created_at = Column(Date, comment="Дата создания")
    updated_at = Column(Date, comment="Дата обновления")
    
    # Связи
    user = relationship("User", back_populates="habits")
    # logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")  # Убираем, чтобы избежать цикла
    
    # Ограничения на уровне БД
    __table_args__ = (
        CheckConstraint(
            "frequency IN ('daily', 'weekly', 'custom')",
            name="check_frequency"
        ),
        CheckConstraint(
            "goal > 0 AND goal <= 50",
            name="check_goal"
        ),
        CheckConstraint(
            "length(name) > 0",
            name="check_name_length"
        ),
        CheckConstraint(
            "color IN ('blue', 'green', 'red', 'yellow', 'purple', 'orange')",
            name="check_color"
        ),
    )
    
    def __repr__(self):
        return f"<Habit(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    def to_dict(self):
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "goal": self.goal,
            "streak_current": self.streak_current,
            "last_completed_date": self.last_completed_date.isoformat() if self.last_completed_date else None,
            "color": self.color,
            "reminder_time": self.reminder_time.isoformat() if self.reminder_time else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def is_completed_today(self) -> bool:
        """Выполнена ли привычка сегодня"""
        if not self.last_completed_date:
            return False
        return self.last_completed_date == date.today()
    
    @property
    def streak_emoji(self) -> str:
        """Эмодзи для стрика"""
        if self.streak_current >= 30:
            return "🔥"
        elif self.streak_current >= 7:
            return "💪"
        elif self.streak_current >= 3:
            return "👍"
        else:
            return "🌱"
    
    def increment_streak(self):
        """Увеличить стрик на 1"""
        self.streak_current += 1
        self.last_completed_date = date.today()
    
    def reset_streak(self):
        """Сбросить стрик"""
        self.streak_current = 0
