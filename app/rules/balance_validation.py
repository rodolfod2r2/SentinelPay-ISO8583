"""4. Saldo por categoria (e transbordo se permitido)."""
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.rules.base import ValidationContext, ValidationHandler, ValidationResult
from app.models.balance import CardBalance
from app.models.tenant import TenantTransbordo


class BalanceValidationHandler(ValidationHandler):
    """Verifica saldo da categoria principal; se insuficiente, tenta transbordo."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _validate(self, ctx: ValidationContext) -> ValidationResult | None:
        if ctx.card is None or ctx.category_key is None:
            return None
        amount = Decimal(ctx.amount_minor) / 100

        # Saldo da categoria principal
        stmt = select(CardBalance).where(
            CardBalance.card_id == ctx.card.id,
            CardBalance.category_key == ctx.category_key,
        )
        r = await self.db.execute(stmt)
        main_balance = r.scalar_one_or_none()
        main_saldo = main_balance.balance if main_balance else Decimal("0")

        if main_saldo >= amount:
            return None  # aprovado neste passo; segue para antifraude

        # Transbordo: verificar se tenant permite usar saldo reserva
        stmt_t = select(TenantTransbordo).where(
            TenantTransbordo.tenant_id == ctx.tenant_id,
            TenantTransbordo.category_key == ctx.category_key,
            TenantTransbordo.allowed == True,
        )
        r_t = await self.db.execute(stmt_t)
        transbordo_rules = r_t.scalars().all()
        for rule in transbordo_rules:
            stmt_b = select(CardBalance).where(
                CardBalance.card_id == ctx.card.id,
                CardBalance.category_key == rule.reserve_category_key,
            )
            r_b = await self.db.execute(stmt_b)
            reserve = r_b.scalar_one_or_none()
            reserve_saldo = reserve.balance if reserve else Decimal("0")
            total = main_saldo + reserve_saldo
            if total >= amount:
                ctx.reserve_category_key = rule.reserve_category_key
                return None  # aprovado com transbordo
        # Saldo insuficiente
        return ValidationResult(
            approved=False,
            response_code="51",
            message="Insufficient balance",
        )
