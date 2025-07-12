from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from src.core.database import Base

class Waitlist(Base):
    __tablename__ = "waitlist"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    is_notified = Column(Boolean, default=False)
    referrer = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Waitlist(email={self.email}, created_at={self.created_at})>"
