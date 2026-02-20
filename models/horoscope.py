from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from core.database import Base
from datetime import date

class HoroscopeCache(Base):
    __tablename__ = "horoscope_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    zodiac_sign = Column(String(20), nullable=False)  # Овен, Телец и т.д.
    horoscope_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    content = Column(Text, nullable=False)  # Текст гороскопа
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<HoroscopeCache(sign={self.zodiac_sign}, date={self.horoscope_date})>"
