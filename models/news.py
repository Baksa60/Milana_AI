from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class NewsSource(Base):
    __tablename__ = "news_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)  # RSS URL или API endpoint
    category = Column(String(50), nullable=False)  # it, crypto, sports, etc.
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    digests = relationship("NewsDigest", back_populates="source")
    
    def __repr__(self):
        return f"<NewsSource(name='{self.name}', category='{self.category}')>"

class NewsDigest(Base):
    __tablename__ = "news_digests"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("news_sources.id"), nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)  # AI-саммари
    original_text = Column(Text, nullable=False)  # Полный текст новости
    url = Column(String(1000), nullable=True)  # Ссылка на новость
    published_at = Column(DateTime(timezone=True), nullable=False)
    digest_date = Column(String(10), nullable=False)  # YYYY-MM-DD для группировки
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    source = relationship("NewsSource", back_populates="digests")
    
    def __repr__(self):
        return f"<NewsDigest(title='{self.title[:50]}...', date={self.digest_date})>"
