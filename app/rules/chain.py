"""Montagem da Chain of Responsibility."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.rules.base import ValidationHandler
from app.rules.message_integrity import MessageIntegrityHandler
from app.rules.card_status import CardStatusHandler
from app.rules.mcc_validation import MccValidationHandler
from app.rules.balance_validation import BalanceValidationHandler
from app.rules.antifraud import AntifraudHandler


def build_validation_chain(
    db: AsyncSession,
    velocity_check_fn=None,
) -> ValidationHandler:
    """
    Ordem: 1. Integridade -> 2. Status do Cartão -> 3. MCC -> 4. Saldo -> 5. Antifraude.
    """
    h1 = MessageIntegrityHandler()
    h2 = CardStatusHandler()
    h3 = MccValidationHandler(db)
    h4 = BalanceValidationHandler(db)
    h5 = AntifraudHandler(velocity_check_fn)

    h1.set_next(h2).set_next(h3).set_next(h4).set_next(h5)
    return h1
