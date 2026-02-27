"""Estratégia Mastercard - mapeamento ISO 8583."""
from app.strategies.base import OperatorStrategy
from app.schemas.iso_8583 import ISO8583Payload


class MastercardStrategy(OperatorStrategy):
    @property
    def operadora_name(self) -> str:
        return "Mastercard"

    def normalize_pan(self, raw_pan: str) -> str:
        return "".join(c for c in raw_pan if c.isdigit())

    def amount_to_minor_units(self, de4: str) -> int:
        s = de4.strip().replace(",", "").replace(".", "")
        if "." in de4 or "," in de4:
            parts = de4.replace(",", ".").split(".")
            if len(parts) == 2:
                return int(parts[0].replace(".", "").replace(",", "")) * 100 + int(
                    (parts[1] + "00")[:2]
                )
        return int(s) if s.isdigit() else 0
