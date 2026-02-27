"""Models de saldo por categoria (bolsos)."""
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.card import Card


class BalanceCategory(Base):
    """Categorias de saldo disponíveis no sistema (refeicao, transporte, livre, etc)."""
    __tablename__ = "balance_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_reserve: Mapped[bool] = mapped_column(default=False)  # pode ser usado em transbordo


class CardBalance(Base):
    """Saldo por categoria por cartão."""
    __tablename__ = "card_balances"
    __table_args__ = (
        UniqueConstraint("card_id", "category_key", name="uq_card_category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), nullable=False
    )
    category_key: Mapped[str] = mapped_column(String(64), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"), nullable=False)

    card: Mapped["Card"] = relationship("Card", back_populates="balances")
