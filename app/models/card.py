"""Model Card - cartão de benefícios."""
import uuid
from datetime import date
from sqlalchemy import String, Date, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class CardStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    PENDING = "pending"


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    pan_masked: Mapped[str] = mapped_column(String(19), nullable=False, index=True)  # últimos 4 + mask
    pan_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)  # hash para busca
    status: Mapped[CardStatus] = mapped_column(
        Enum(CardStatus), default=CardStatus.ACTIVE, nullable=False
    )
    valid_thru: Mapped[date | None] = mapped_column(Date, nullable=True)

    client: Mapped["Client"] = relationship("Client", back_populates="cards")
    balances: Mapped[list["CardBalance"]] = relationship(
        "CardBalance", back_populates="card", cascade="all, delete-orphan"
    )
    transaction_logs: Mapped[list["TransactionLog"]] = relationship(
        "TransactionLog", back_populates="card", cascade="all, delete-orphan"
    )
