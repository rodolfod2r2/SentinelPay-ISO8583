"""2. Status do cartão (ativo, bloqueado, etc)."""
from app.rules.base import ValidationContext, ValidationHandler, ValidationResult
from app.models.card import CardStatus


class CardStatusHandler(ValidationHandler):
    """Cartão deve existir e estar ativo. Contexto.card deve ser preenchido antes."""

    async def _validate(self, ctx: ValidationContext) -> ValidationResult | None:
        if ctx.card is None:
            return ValidationResult(
                approved=False,
                response_code="78",
                message="Card not found",
            )
        if ctx.card.status != CardStatus.ACTIVE:
            if ctx.card.status == CardStatus.BLOCKED:
                return ValidationResult(
                    approved=False,
                    response_code="78",
                    message="Card blocked",
                )
            if ctx.card.status == CardStatus.CANCELLED:
                return ValidationResult(
                    approved=False,
                    response_code="78",
                    message="Card cancelled",
                )
            return ValidationResult(
                approved=False,
                response_code="78",
                message="Card not active",
            )
        return None
