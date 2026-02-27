"""Interface Strategy para operadoras - mapeamento de campos ISO 8583."""
from abc import ABC, abstractmethod
from app.schemas.iso_8583 import ISO8583Payload


class OperatorStrategy(ABC):
    """Estratégia por operadora: normalização e validação dos campos ISO."""

    @property
    @abstractmethod
    def operadora_name(self) -> str:
        pass

    @abstractmethod
    def normalize_pan(self, raw_pan: str) -> str:
        """Retorna PAN apenas dígitos, sem espaços."""
        pass

    @abstractmethod
    def amount_to_minor_units(self, de4: str) -> int:
        """Converte DE4 para valor em centavos (minor units)."""
        pass

    def validate_mti(self, mti: str) -> bool:
        """Valida MTI para mensagem de autorização (0100/0110)."""
        return mti in ("0100", "0110", "0200", "0210")

    def extract_iso_context(self, payload: ISO8583Payload) -> dict:
        """Extrai contexto normalizado para a esteira de validação."""
        return {
            "mti": payload.mti,
            "pan": self.normalize_pan(payload.de2_pan),
            "amount_minor": self.amount_to_minor_units(payload.de4_amount),
            "mcc": payload.de18_mcc.strip(),
            "merchant_id": (payload.de42_merchant_id or "").strip(),
            "currency": payload.de49_currency or "986",
        }


def get_operator_strategy(operadora: str) -> OperatorStrategy:
    """Factory: retorna estratégia da operadora."""
    from app.strategies.visa import VisaStrategy
    from app.strategies.mastercard import MastercardStrategy
    from app.strategies.elo import EloStrategy

    strategies = {
        "visa": VisaStrategy(),
        "mastercard": MastercardStrategy(),
        "master": MastercardStrategy(),
        "elo": EloStrategy(),
    }
    key = operadora.lower().strip()
    if key not in strategies:
        raise ValueError(f"Operadora não suportada: {operadora}. Use: visa, mastercard, elo")
    return strategies[key]
