from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    target_days = Column(Integer, default=30)  # Цель: дней подряд
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="habits")
    records = relationship("HabitRecord", back_populates="habit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Habit(name='{self.name}', streak={self.current_streak})>"

class HabitRecord(Base):
    __tablename__ = "habit_records"
    
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    note = Column(Text, nullable=True)  # Заметка пользователя
    
    # Связи
    habit = relationship("Habit", back_populates="records")
    
    def __repr__(self):
        return f"<HabitRecord(habit_id={self.habit_id}, date={self.completed_at.date()})>"
