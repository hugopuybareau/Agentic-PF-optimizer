from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .portfolio import Portfolio

class Asset(Base):
    __tablename__ = "assets"

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

    symbol: Mapped[str] = mapped_column(String, index=True, nullable=False)
    asset_type: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(precision=20, scale=8), nullable=False)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    portfolio: Mapped[Portfolio] = relationship(
        back_populates="assets",
        lazy="selectin",
    )
