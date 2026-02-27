"""Serviço de débito de saldo por categoria (e transbordo)."""
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.balance import CardBalance


class BalanceService:
    """Débito em saldo do cartão por categoria."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def debit(
        self,
        card_id: UUID,
        category_key: str,
        amount: Decimal,
        reserve_category_key: str | None = None,
        reserve_amount: Decimal | None = None,
    ) -> None:
        """
        Debita valor da categoria principal; se reserve_* informado, debita o restante da reserva.
        """
        stmt = select(CardBalance).where(
            CardBalance.card_id == card_id,
            CardBalance.category_key == category_key,
        )
        r = await self.db.execute(stmt)
        main = r.scalar_one_or_none()
        if main is None:
            main = CardBalance(
                card_id=card_id,
                category_key=category_key,
                balance=Decimal("0"),
            )
            self.db.add(main)
        main.balance -= amount
        if main.balance < 0:
            main.balance = Decimal("0")

        if reserve_category_key and reserve_amount and reserve_amount > 0:
            stmt2 = select(CardBalance).where(
                CardBalance.card_id == card_id,
                CardBalance.category_key == reserve_category_key,
            )
            r2 = await self.db.execute(stmt2)
            reserve = r2.scalar_one_or_none()
            if reserve is None:
                reserve = CardBalance(
                    card_id=card_id,
                    category_key=reserve_category_key,
                    balance=Decimal("0"),
                )
                self.db.add(reserve)
            reserve.balance -= reserve_amount
            if reserve.balance < 0:
                reserve.balance = Decimal("0")

        await self.db.flush()
