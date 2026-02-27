"""3. Validação de MCC/Categoria - MCC permitido e mapeamento para bolso."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.rules.base import ValidationContext, ValidationHandler, ValidationResult
from app.models.tenant import TenantMccCategory


class MccValidationHandler(ValidationHandler):
    """Verifica se o MCC é permitido para o tenant e define category_key (bolso)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _validate(self, ctx: ValidationContext) -> ValidationResult | None:
        stmt = select(TenantMccCategory).where(
            TenantMccCategory.tenant_id == ctx.tenant_id,
            TenantMccCategory.mcc == ctx.mcc,
        )
        result = await self.db.execute(stmt)
        mcc_cat = result.scalars().first()
        if mcc_cat is None:
            return ValidationResult(
                approved=False,
                response_code="58",
                message="MCC not allowed for tenant",
            )
        ctx.category_key = mcc_cat.category_key
        return None
