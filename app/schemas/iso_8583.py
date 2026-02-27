"""Schema ISO 8583 em formato JSON para entrada na API."""
from pydantic import BaseModel, Field


class ISO8583Payload(BaseModel):
    """Mapeamento dos elementos ISO 8583 usados na autorização."""

    mti: str = Field(..., description="Message Type Indicator")
    de2_pan: str = Field(..., min_length=13, max_length=19, description="PAN - Primary Account Number")
    de4_amount: str = Field(..., description="Valor da transação (centavos ou valor)")
    de18_mcc: str = Field(..., min_length=4, max_length=4, description="Merchant Category Code - Categoria do lojista")
    de42_merchant_id: str | None = Field(None, description="Merchant ID")
    de48_cvv: str | None = Field(None, description="CVV")
    de49_currency: str = Field("986", description="Código da moeda (ISO 4217 numérico)")
