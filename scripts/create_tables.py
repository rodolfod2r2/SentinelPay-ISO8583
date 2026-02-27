"""
Script para criar todas as tabelas no banco (Base.metadata.create_all).
Uso: python -m scripts.create_tables
Requer DATABASE_URL no .env (ou variável de ambiente) em formato async:
  postgresql+asyncpg://user:pass@host:5432/dbname
"""
import asyncio
import os
import sys

# Garante que o root do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db


async def main():
    await init_db()
    print("Tabelas criadas com sucesso.")


if __name__ == "__main__":
    asyncio.run(main())
