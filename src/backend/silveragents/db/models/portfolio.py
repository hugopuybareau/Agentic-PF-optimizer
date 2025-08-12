# backend/app/db/models/portfolio.py

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ...db.base import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="portfolios")
    alerts = relationship("Alert", back_populates="portfolio", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="portfolio", cascade="all, delete-orphan")
    digests = relationship("Digest", back_populates="portfolio", cascade="all, delete-orphan")
    news_items = relationship("NewsItem", back_populates="portfolio", cascade="all, delete-orphan")
