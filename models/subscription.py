from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from datetime import date

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)  # Цена в рублях
    billing_cycle = Column(String(20), nullable=False)  # monthly, yearly, weekly
    next_payment_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    reminder_days_before = Column(Integer, default=3)  # За сколько дней напоминать
    category = Column(String(50), default="other")  # entertainment, work, education, other
    is_trial = Column(Boolean, default=False)  # Это бесплатный триал?
    trial_end_date = Column(Date, nullable=True)  # Когда заканчивается триал
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="subscriptions")
    
    @property
    def days_until_payment(self) -> int:
        """Сколько дней до следующего платежа"""
        if not self.next_payment_date:
            return 0
        delta = self.next_payment_date - date.today()
        return max(0, delta.days)
    
    @property
    def is_trial_active(self) -> bool:
        """Активен ли триал"""
        if not self.is_trial or not self.trial_end_date:
            return False
        return date.today() <= self.trial_end_date
    
    def __repr__(self):
        return f"<Subscription(name='{self.name}', price={self.price}₽, next_payment={self.next_payment_date})>"
