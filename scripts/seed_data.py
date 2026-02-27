"""
Seed opcional: cria um tenant, cliente, cartão e saldos para testes.
Uso: python -m scripts.seed_data
"""
import asyncio
import os
import sys
from decimal import Decimal
from uuid import uuid4
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.models import Tenant, TenantMccCategory, TenantTransbordo, Client, Card, CardBalance
from app.models.card import CardStatus


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Tenant
        tenant_id = uuid4()
        tenant = Tenant(id=tenant_id, name="Tenant Demo", active=True)
        db.add(tenant)

        # MCC Refeição (5812) -> refeicao
        db.add(TenantMccCategory(tenant_id=tenant_id, mcc="5812", category_key="refeicao", description="Restaurantes"))
        # MCC Transporte (4121) -> transporte
        db.add(TenantMccCategory(tenant_id=tenant_id, mcc="4121", category_key="transporte", description="Transporte"))
        # Transbordo: refeicao pode usar livre
        db.add(TenantTransbordo(tenant_id=tenant_id, category_key="refeicao", reserve_category_key="livre", allowed=True))

        # Cliente e cartão (PAN de teste: 4111111111111111)
        client = Client(tenant_id=tenant_id, external_id="EXT001", name="Cliente Teste")
        db.add(client)
        await db.flush()

        pan = "4111111111111111"
        pan_hash = hashlib.sha256(pan.encode()).hexdigest()
        card = Card(
            tenant_id=tenant_id,
            client_id=client.id,
            pan_masked="************1111",
            pan_hash=pan_hash,
            status=CardStatus.ACTIVE,
        )
        db.add(card)
        await db.flush()

        db.add(CardBalance(card_id=card.id, category_key="refeicao", balance=Decimal("500.00")))
        db.add(CardBalance(card_id=card.id, category_key="livre", balance=Decimal("200.00")))

        await db.commit()
        print("Seed concluído.")
        print("Tenant ID (use no metadata.tenant_id):", tenant_id)
        print("PAN de teste:", pan)
        print("MCC 5812 = refeicao; saldo refeicao=500, livre=200 (transbordo permitido).")


if __name__ == "__main__":
    asyncio.run(seed())
