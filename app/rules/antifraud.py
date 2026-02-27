"""5. Antifraude - Velocity Check via Redis."""
from app.rules.base import ValidationContext, ValidationHandler, ValidationResult


class AntifraudHandler(ValidationHandler):
    """Velocity check: muitas transações em curto período = rejeitar."""

    def __init__(self, velocity_check_fn):
        """
        velocity_check_fn: async (pan_hash: str, amount_minor: int, window_seconds: int) -> bool
        Retorna True se passar (sem excesso de velocidade), False para bloquear.
        """
        self.velocity_check_fn = velocity_check_fn

    async def _validate(self, ctx: ValidationContext) -> ValidationResult | None:
        if not self.velocity_check_fn:
            return None
        try:
            from app.config import get_settings
            settings = get_settings()
            ok = await self.velocity_check_fn(
                ctx.pan_hash,
                ctx.amount_minor,
                settings.velocity_window_seconds,
            )
            if not ok:
                return ValidationResult(
                    approved=False,
                    response_code="65",
                    message="Velocity check failed",
                )
        except Exception:
            # Se Redis indisponível, não bloquear por padrão (fail-open)
            pass
        return None
