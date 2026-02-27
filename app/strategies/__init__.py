"""Strategy para operadoras - mapeamento ISO 8583 por bandeira."""
from app.strategies.base import OperatorStrategy, get_operator_strategy
from app.strategies.visa import VisaStrategy
from app.strategies.mastercard import MastercardStrategy
from app.strategies.elo import EloStrategy

__all__ = [
    "OperatorStrategy",
    "get_operator_strategy",
    "VisaStrategy",
    "MastercardStrategy",
    "EloStrategy",
]
