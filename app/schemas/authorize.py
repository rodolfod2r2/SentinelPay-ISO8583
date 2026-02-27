"""Schemas do endpoint de autorização."""
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.iso_8583 import ISO8583Payload


class AuthorizeMetadata(BaseModel):
    tenant_id: UUID
    operadora: str = Field(..., description="Visa | Mastercard | Elo")


class AuthorizeRequest(BaseModel):
    metadata: AuthorizeMetadata
    iso_8583: ISO8583Payload


class AuthorizeResponse(BaseModel):
    approved: bool
    response_code: str = Field(..., description="DE39 - Código de resposta")
    message: str | None = None
    category_used: str | None = Field(None, description="Categoria de saldo utilizada")
    transaction_id: str | None = None
