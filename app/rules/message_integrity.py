"""1. Integridade da mensagem ISO 8583."""
from app.rules.base import ValidationContext, ValidationHandler, ValidationResult


class MessageIntegrityHandler(ValidationHandler):
    """Valida presença e formato mínimo dos campos obrigatórios."""

    async def _validate(self, ctx: ValidationContext) -> ValidationResult | None:
        if not ctx.pan or len(ctx.pan) < 13:
            return ValidationResult(
                approved=False,
                response_code="14",
                message="Invalid PAN",
            )
        if ctx.amount_minor <= 0:
            return ValidationResult(
                approved=False,
                response_code="13",
                message="Invalid amount",
            )
        if not ctx.mcc or len(ctx.mcc) != 4 or not ctx.mcc.isdigit():
            return ValidationResult(
                approved=False,
                response_code="22",
                message="Invalid MCC",
            )
        if not ctx.currency or len(ctx.currency) != 3:
            return ValidationResult(
                approved=False,
                response_code="54",
                message="Invalid currency",
            )
        return None
