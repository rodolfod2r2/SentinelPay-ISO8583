"""Base da Chain of Responsibility - contexto e handler."""
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class ValidationResult:
    """Resultado de um passo da validação."""
    approved: bool
    response_code: str  # DE39
    message: str | None = None
    category_used: str | None = None  # categoria de saldo utilizada


@dataclass
class ValidationContext:
    """Contexto passado ao longo da cadeia de validação."""
    tenant_id: UUID
    # Dados normalizados ISO (após strategy)
    pan: str
    pan_hash: str
    amount_minor: int
    mcc: str
    merchant_id: str
    currency: str
    mti: str
    # Entidades carregadas (preenchidas pelos handlers)
    card: Any = None
    category_key: str | None = None  # categoria principal para o MCC
    reserve_category_key: str | None = None  # transbordo
    # Resultado final
    result: ValidationResult | None = None
    # Raw para log
    raw_request: dict = field(default_factory=dict)


class ValidationHandler:
    """Handler base da Chain of Responsibility."""

    _next: "ValidationHandler | None" = None

    def set_next(self, handler: "ValidationHandler") -> "ValidationHandler":
        self._next = handler
        return handler

    async def handle(self, ctx: ValidationContext) -> ValidationContext:
        """Executa esta validação; se aprovado, chama o próximo."""
        result = await self._validate(ctx)
        if result is not None:
            ctx.result = result
            return ctx
        if self._next is None:
            ctx.result = ValidationResult(
                approved=True,
                response_code="00",
                message="Approved",
            )
            return ctx
        return await self._next.handle(ctx)

    async def _validate(self, ctx: ValidationContext) -> ValidationResult | None:
        """Retorna ValidationResult em caso de rejeição; None para seguir."""
        raise NotImplementedError
