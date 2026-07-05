from sqlalchemy import Column, Integer, String, DateTime, text
from src.db import Base

class ContactMessage(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

# Alias for backward compatibility with contact router
Contact = ContactMessage

class SyncEventHistory(Base):
    __tablename__ = "sync_events_history"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String, nullable=False, index=True)
    event = Column(String, nullable=False)
    payload = Column(String, nullable=False) # JSON serialized string
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
