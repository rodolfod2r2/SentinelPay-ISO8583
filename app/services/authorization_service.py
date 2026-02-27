"""Serviço de autorização: orquestra Strategy + Chain + débito + log."""
import hashlib
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import Card
from app.models.transaction_log import TransactionLog
from app.models.balance import CardBalance
from app.rules.base import ValidationContext, ValidationResult
from app.rules.chain import build_validation_chain
from app.schemas.authorize import AuthorizeRequest, AuthorizeResponse
from app.strategies.base import get_operator_strategy
from app.services.balance_service import BalanceService
from app.config import get_settings


def _pan_hash(pan: str) -> str:
    return hashlib.sha256(pan.encode()).hexdigest()


class AuthorizationService:
    """Motor de autorização: valida e persiste resultado."""

    def __init__(self, db: AsyncSession):
        self.db = db
        settings = get_settings()
        try:
            from app.services.redis_velocity_service import RedisVelocityService
            self._velocity_svc = RedisVelocityService(
                settings.redis_url, settings.velocity_window_seconds
            )
            self._velocity_check_fn = self._velocity_svc.check
        except Exception:
            self._velocity_svc = None
            self._velocity_check_fn = None

    async def authorize(self, request: AuthorizeRequest) -> AuthorizeResponse:
        metadata = request.metadata
        iso = request.iso_8583
        tenant_id = metadata.tenant_id
        operadora = metadata.operadora

        strategy = get_operator_strategy(operadora)
        ctx_dict = strategy.extract_iso_context(iso)
        pan_hash = _pan_hash(ctx_dict["pan"])

        stmt = select(Card).where(
            Card.tenant_id == tenant_id,
            Card.pan_hash == pan_hash,
        )
        r = await self.db.execute(stmt)
        card = r.scalars().first()

        ctx = ValidationContext(
            tenant_id=tenant_id,
            pan=ctx_dict["pan"],
            pan_hash=pan_hash,
            amount_minor=ctx_dict["amount_minor"],
            mcc=ctx_dict["mcc"],
            merchant_id=ctx_dict["merchant_id"],
            currency=ctx_dict["currency"],
            mti=ctx_dict["mti"],
            raw_request=request.model_dump(mode="json"),
        )
        ctx.card = card

        chain = build_validation_chain(self.db, self._velocity_check_fn)
        ctx = await chain.handle(ctx)

        result = ctx.result or ValidationResult(
            approved=True, response_code="00", message="Approved"
        )
        approved = result.approved
        response_code = result.response_code
        category_used = ctx.category_key if approved else None

        log = TransactionLog(
            card_id=card.id if card else None,
            amount=Decimal(ctx.amount_minor) / 100,
            currency=ctx.currency,
            mcc=ctx.mcc,
            merchant_id=ctx.merchant_id or None,
            approved=approved,
            response_code=response_code,
            category_used=category_used,
            raw_request=ctx.raw_request,
        )
        self.db.add(log)
        await self.db.flush()

        if approved and card:
            amount_dec = Decimal(ctx.amount_minor) / 100
            balance_svc = BalanceService(self.db)
            if ctx.reserve_category_key:
                stmt_m = select(CardBalance).where(
                    CardBalance.card_id == card.id,
                    CardBalance.category_key == ctx.category_key,
                )
                rm = await self.db.execute(stmt_m)
                main_bal = rm.scalar_one_or_none()
                main_saldo = main_bal.balance if main_bal else Decimal("0")
                main_debit = min(main_saldo, amount_dec)
                reserve_debit = amount_dec - main_debit
                await balance_svc.debit(
                    card.id,
                    ctx.category_key,
                    main_debit,
                    ctx.reserve_category_key,
                    reserve_debit,
                )
            else:
                await balance_svc.debit(card.id, ctx.category_key, amount_dec)

        return AuthorizeResponse(
            approved=approved,
            response_code=response_code,
            message=result.message,
            category_used=category_used,
            transaction_id=str(log.id),
        )
