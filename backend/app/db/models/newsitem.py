from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .asset import Asset
    from .portfolio import Portfolio


class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )

    portfolio_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    asset_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    snippet: Mapped[str | None] = mapped_column(Text)
    sentiment: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    portfolio: Mapped[Portfolio] = relationship(
        back_populates="news_items",
        lazy="selectin",
    )
    asset: Mapped[Asset | None] = relationship(
        lazy="selectin",
    )
