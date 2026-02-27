"""Model Tenant - isolamento multitenant e regras por operadora."""
import uuid
from sqlalchemy import String, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # regras extras

    mcc_categories: Mapped[list["TenantMccCategory"]] = relationship(
        "TenantMccCategory", back_populates="tenant", cascade="all, delete-orphan"
    )
    transbordo_rules: Mapped[list["TenantTransbordo"]] = relationship(
        "TenantTransbordo", back_populates="tenant", cascade="all, delete-orphan"
    )


class TenantMccCategory(Base):
    """MCC permitido por tenant -> categoria de saldo (bolso)."""
    __tablename__ = "tenant_mcc_categories"
    __table_args__ = (UniqueConstraint("tenant_id", "mcc", name="uq_tenant_mcc"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    mcc: Mapped[str] = mapped_column(String(4), nullable=False)  # DE18
    category_key: Mapped[str] = mapped_column(String(64), nullable=False)  # refeicao, transporte, livre
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="mcc_categories")


class TenantTransbordo(Base):
    """Regra de transbordo: categoria principal pode usar saldo da categoria reserva."""
    __tablename__ = "tenant_transbordo"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "category_key", "reserve_category_key",
            name="uq_tenant_transbordo",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    category_key: Mapped[str] = mapped_column(String(64), nullable=False)
    reserve_category_key: Mapped[str] = mapped_column(String(64), nullable=False)
    allowed: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="transbordo_rules")
