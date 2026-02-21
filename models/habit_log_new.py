"""
Модель логов выполнений привычек
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from models import Base

class HabitLog(Base):
    """Модель логов выполнений привычек"""
    __tablename__ = "habit_logs"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, comment="Дата выполнения")
    completed_at = Column(DateTime, default=datetime.utcnow, comment="Точное время выполнения")
    
    # Убираем relationship чтобы избежать циклического импорта
    # habit = relationship("Habit", back_populates="logs")
    
    # Уникальный индекс - защита от дублей
    __table_args__ = (
        UniqueConstraint('habit_id', 'date', name='uq_habit_date'),
    )
    
    def __repr__(self):
        return f"<HabitLog(id={self.id}, habit_id={self.habit_id}, date={self.date})>"
    
    def to_dict(self):
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "completed_at": self.completed_at.isoformat()
        }
